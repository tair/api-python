#!/usr/bin/python
"""
TAIR3-633: Daily cron to replenish 50 free usage units for eligible ORCID-linked TAIR accounts.
TAIR3-890: also self-heals accounts whose free-unit grant silently failed at ORCID-link time.

Eligibility (ORCID still linked + TAIR credential in all cases). Each account is
classified into one of three actions:

1. REPLENISH - has an OrcidCreditTracking row whose credit_reissue_date has passed.
   Adds 50 units, pushes free_expiry_date and credit_reissue_date out a year, and
   sends the annual replenishment email. (Original TAIR3-633 behaviour.)

2. ENROLL - has NO OrcidCreditTracking row and no active free units, i.e. the grant
   at ORCID-link time never happened (TAIR3-890). Adds 50 units and creates the
   tracking row. Deliberately sends NO user email: this is a first-time grant, and
   the replenishment wording ("your next annual set") would be wrong. These appear
   in the admin report instead.

3. REPAIR - has NO OrcidCreditTracking row but DOES have active free units, i.e. the
   grant partially succeeded (bucket written, tracking row not). Creates the missing
   tracking row aligned to the existing free_expiry_date and grants NO units, so the
   account is not double-credited. No user email.

Actions 2 and 3 run as part of the normal nightly job, so a grant that fails at
ORCID-link time is corrected within a day and the accounts already affected are
picked up on the first run. Both only ever touch accounts that are entitled to
units but do not have them; --no-heal restricts the run to action 1 if needed.

Admin email policy: the admin report is sent ONLY when a run needs attention -
any account failed, or an enroll/repair happened (both mean the grant at
ORCID-link time is still broken). A run that just does its scheduled top-ups
sends no admin email. An unhandled abort (e.g. DB down) also emails.
User-facing replenishment emails are unaffected and still go out per account.

Every run publishes CloudWatch metrics (namespace PhoenixJobs, dimension
Job=OrcidCreditReplenish): RunSuccess, Replenished, Enrolled, Repaired, Failed.
RunSuccess backs the "job stopped running" alarm, which treats a missing
datapoint as breaching - so a cron that never fires alarms like a failure.
If the publish fails the run is appended to
/var/log/api/orcid_replenish_history.tsv as a local fallback.

Usage:
  python scripts/replenishOrcidCredits.py                    # nightly: replenish + self-heal
  python scripts/replenishOrcidCredits.py --dry-run
  python scripts/replenishOrcidCredits.py --no-heal          # action 1 only
  python scripts/replenishOrcidCredits.py --orcid 0009-0000-0624-7467   # single ORCID only

Run once per day via cron, e.g.:
  0 3 * * * cd /var/www/api-python && python scripts/replenishOrcidCredits.py >> /var/log/api/orcid_replenish.log 2>&1
"""
import MySQLdb
import os
import sys
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# Logging: every line prefixed with timestamp
# -----------------------------------------------------------------------------
def log(msg):
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg)

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
UNITS_TO_ADD = 50
REPLENISH_DAYS = 365

EMAIL_SUBJECT = "Your annual complimentary TAIR usage units have been replenished"
EMAIL_FROM = "Phoenix Bioinformatics <info@phoenixbioinformatics.org>"
REPORT_RECIPIENT = "swapnil.sawant@arabidopsis.org"

# The admin report is sent ONLY when a run needs attention (see run_has_issue).
# Every run - clean or not - publishes CloudWatch metrics instead, so "did it
# run?" is answerable without an email for every quiet night.
#
# This box (AWS account 582474249410) carries the EC2Role4CloudWatch instance
# role, which grants PutMetricData and nothing else - it can publish but cannot
# read metrics or manage alarms. The alarm lives in that account, created out
# of band. RunSuccess is the dead-man's switch: a MISSING datapoint is treated
# as breaching, so a cron that never fires alarms like a failure.
CW_NAMESPACE = "PhoenixJobs"
CW_JOB = "OrcidCreditReplenish"
CW_REGION = "us-west-2"
AWS_CLI = "/usr/bin/aws"

# Local fallback, written only when the CloudWatch publish fails, so a run is
# never left with no record at all.
HISTORY_FILE = "/var/log/api/orcid_replenish_history.tsv"
HISTORY_HEADER = "timestamp\tstatus\teligible\tok\tfail\treplenished\tenrolled\trepaired\tnote"
EMAIL_BODY_TEMPLATE = """\
Dear TAIR user,

Because you've linked your ORCID to your TAIR account, we've just added your next annual set of 50 complimentary TAIR usage units. These units are intended to support infrequent or exploratory use of TAIR, and they are replenished annually as long as your ORCID remains connected.

TAIR is sustained primarily through institutional and organizational subscriptions, which support ongoing curation, infrastructure, and development. Offering complimentary units is one way we try to keep TAIR accessible while balancing long-term sustainability.

You can view your current usage and unit balance by logging into your TAIR account at:
https://www.arabidopsis.org/profile

If you or your institution rely on TAIR regularly, you can learn more about subscription options on the TAIR website.

Best regards,
The TAIR Team
"""

def bootstrap_django():
    """Load Django so we can use settings + send_mail from the current instance."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
    import django
    django.setup()
    from django.conf import settings
    return settings


# -----------------------------------------------------------------------------
# Query: eligible accounts
# -----------------------------------------------------------------------------
ELIGIBLE_QUERY = """
SELECT
    o.orcid_id,
    c.partyId AS party_id,
    c.email,
    c.username,
    u.user_usage_id,
    u.total_units,
    u.remaining_units,
    u.free_expiry_date,
    t.orcid_id AS tracking_orcid,
    t.credit_reissue_date
FROM OrcidCredentials o
JOIN Credential c ON o.CredentialId = c.id
LEFT JOIN UserBucketUsage u ON c.partyId = u.partyId_id
LEFT JOIN OrcidCreditTracking t ON o.orcid_id = t.orcid_id
WHERE o.orcid_id IS NOT NULL
  AND o.orcid_id != ''
  AND c.partnerId = 'tair'
  AND (%(eligibility)s)
ORDER BY o.orcid_id
"""

# Accounts already enrolled whose reissue date has passed - the nightly case.
REPLENISH_ELIGIBILITY = """t.orcid_id IS NOT NULL
       AND t.credit_reissue_date IS NOT NULL
       AND t.credit_reissue_date <= NOW()"""

# Adds accounts that were never enrolled (grant silently failed). Default; off with --no-heal.
HEAL_ELIGIBILITY = REPLENISH_ELIGIBILITY + """
    OR t.orcid_id IS NULL"""


def build_eligible_query(heal):
    return ELIGIBLE_QUERY % {
        'eligibility': HEAL_ELIGIBILITY if heal else REPLENISH_ELIGIBILITY
    }


def fetch_eligible(cur, orcid_id=None, heal=False):
    query = build_eligible_query(heal)
    if orcid_id:
        q = query.replace("ORDER BY o.orcid_id", "AND o.orcid_id = %s\nORDER BY o.orcid_id")
        cur.execute(q, (orcid_id,))
    else:
        cur.execute(query)
    return cur.fetchall()


def send_notification_email(to_email, username):
    """Send the replenishment notification using Django send_mail (same as rest of repo)."""
    if not to_email or not str(to_email).strip():
        log("  [skip email] No email for user %s" % username)
        return False
    try:
        from django.core.mail import send_mail
        send_mail(
            subject=EMAIL_SUBJECT,
            message=EMAIL_BODY_TEMPLATE,
            from_email=EMAIL_FROM,
            recipient_list=[to_email.strip()],
            fail_silently=False,
        )
        return True
    except Exception as e:
        log("  [email error] %s: %s" % (to_email, e))
        return False


def run_has_issue(fail, enrolled_list, repaired_list):
    """Does this run need a human to look at it?

    - fail > 0        : an account could not be processed.
    - enrolled > 0    : an ORCID was linked but never got its units, i.e. the grant
                        failed at link time (TAIR3-890). Self-healed here, but the
                        underlying bug is still live.
    - repaired > 0    : units were granted but the tracking row was not written -
                        same link-time bug, partial version.

    A plain replenishment run (units topped up on schedule, users emailed) is the
    normal case and is NOT an issue - it goes to CloudWatch only.
    """
    return fail > 0 or len(enrolled_list) > 0 or len(repaired_list) > 0


def _put_metric(name, value):
    """One PutMetricData call via the AWS CLI. Returns True on success.

    Shelling out rather than using boto: this runs on Python 2.7 under a plain
    /usr/bin/python with no guarantee boto3 is importable, and the CLI already
    picks up the instance role.
    """
    import subprocess
    cmd = [
        AWS_CLI, "cloudwatch", "put-metric-data",
        "--region", CW_REGION,
        "--namespace", CW_NAMESPACE,
        "--metric-name", name,
        "--value", str(value),
        "--unit", "Count",
        "--dimensions", "Job=%s" % CW_JOB,
    ]
    devnull = open(os.devnull, 'w')
    try:
        return subprocess.call(cmd, stdout=devnull, stderr=devnull) == 0
    finally:
        devnull.close()


def publish_run(status, success, eligible, ok, fail, replenished, enrolled, repaired, note=''):
    """Publish this run's outcome to CloudWatch; fall back to HISTORY_FILE.

    This is the "did the job run?" record that replaces the nightly success email.
    Best-effort: a bookkeeping failure must never fail the run or mask work that
    has already committed.
    """
    metrics = [
        ("RunSuccess", success),
        ("Replenished", replenished),
        ("Enrolled", enrolled),
        ("Repaired", repaired),
        ("Failed", fail),
    ]
    try:
        published = all([_put_metric(n, v) for n, v in metrics])
    except Exception as e:
        log("[cloudwatch error] %s" % e)
        published = False

    if published:
        log("CloudWatch: published %s/%s RunSuccess=%d replenished=%d enrolled=%d repaired=%d failed=%d"
            % (CW_NAMESPACE, CW_JOB, success, replenished, enrolled, repaired, fail))
        return
    log("WARNING: CloudWatch publish failed - recording locally in %s" % HISTORY_FILE)
    record_history(status, eligible, ok, fail, replenished, enrolled, repaired,
                   note=('cw-publish-failed; %s' % note) if note else 'cw-publish-failed')


def record_history(status, eligible, ok, fail, replenished, enrolled, repaired, note=''):
    """Append one line per run to HISTORY_FILE (CloudWatch fallback only)."""
    try:
        need_header = not os.path.exists(HISTORY_FILE)
        d = os.path.dirname(HISTORY_FILE)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        f = open(HISTORY_FILE, 'a')
        try:
            if need_header:
                f.write(HISTORY_HEADER + "\n")
            f.write("%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n" % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status,
                eligible, ok, fail, replenished, enrolled, repaired, note))
        finally:
            f.close()
    except Exception as e:
        log("[history write error] %s: %s" % (HISTORY_FILE, e))


def send_report_email(replenished_list, enrolled_list=None, repaired_list=None, fail=0):
    """Send the admin report. Only called when run_has_issue() is true.

    Enrolled/repaired accounts get no user-facing email (TAIR3-890), so this report
    is the only notification that a silently-failed grant was corrected. A non-zero
    enrolled count on an ongoing basis means grants are still failing at link time.
    """
    enrolled_list = enrolled_list or []
    repaired_list = repaired_list or []
    if not replenished_list and not enrolled_list and not repaired_list:
        return
    try:
        from django.core.mail import send_mail
        today = datetime.now().strftime('%Y-%m-%d')

        def section(title, entries, note=''):
            if not entries:
                return ''
            out = "\n%s: %d\n" % (title, len(entries))
            if note:
                out += "%s\n" % note
            out += "-" * 60 + "\n"
            out += "ORCID ID | Email\n"
            for entry in entries:
                out += "%s | %s\n" % (entry['orcid_id'], entry['email'] or '(none)')
            return out

        body = "ORCID credit report for %s\n" % today
        body += ("\nThis email is sent only when a run needs attention. Clean replenish-only\n"
                 "runs publish CloudWatch metrics (%s, Job=%s) and send nothing.\n"
                 % (CW_NAMESPACE, CW_JOB))
        body += "\nfailed=%d  replenished=%d  first-time enrolled=%d  tracking repaired=%d\n" % (
            fail, len(replenished_list), len(enrolled_list), len(repaired_list))
        if fail:
            body += ("\n%d account(s) FAILED to process - see the per-account [error] lines in\n"
                     "/var/log/api/orcid_replenish.log for this run.\n" % fail)
        body += section("Replenished (annual top-up, user emailed)", replenished_list)
        body += section(
            "First-time enrolled (TAIR3-890 - grant had silently failed)", enrolled_list,
            "These accounts had a linked ORCID but no free units. 50 units granted now.\n"
            "No user email was sent. A recurring non-zero count here means grants are\n"
            "still failing during ORCID linking - investigate.")
        body += section(
            "Tracking repaired (TAIR3-890 - units were already present)", repaired_list,
            "Missing OrcidCreditTracking row created; NO units granted (already held active free units).")

        send_mail(
            subject="[ORCID CREDITS] ACTION NEEDED %s - failed %d, enrolled %d, repaired %d" % (
                today, fail, len(enrolled_list), len(repaired_list)),
            message=body,
            from_email=EMAIL_FROM,
            recipient_list=[REPORT_RECIPIENT],
            fail_silently=False,
        )
    except Exception as e:
        log("[report email error] %s" % e)


# -----------------------------------------------------------------------------
# Classification (TAIR3-890)
# -----------------------------------------------------------------------------
ACTION_REPLENISH = 'replenish'   # tracking row exists and reissue date passed
ACTION_ENROLL = 'enroll'         # no tracking row, no active free units -> grant never happened
ACTION_REPAIR = 'repair'         # no tracking row but free units active -> only tracking missing


def classify(row, now):
    if row['tracking_orcid'] is not None:
        return ACTION_REPLENISH
    free_expiry = row['free_expiry_date']
    if row['user_usage_id'] is not None and free_expiry is not None and free_expiry > now:
        return ACTION_REPAIR
    return ACTION_ENROLL


def _add_units(cur, row, expiry_str):
    """Add UNITS_TO_ADD to the account's bucket, creating the bucket if absent."""
    if row['user_usage_id'] is None:
        cur.execute("""
            INSERT INTO UserBucketUsage (partyId_id, partner_id, total_units, remaining_units, free_expiry_date)
            VALUES (%s, 'tair', %s, %s, %s)
        """, (row['party_id'], UNITS_TO_ADD, UNITS_TO_ADD, expiry_str))
        return True
    cur.execute("""
        UPDATE UserBucketUsage
        SET total_units = total_units + %s,
            remaining_units = remaining_units + %s,
            free_expiry_date = %s
        WHERE user_usage_id = %s
    """, (UNITS_TO_ADD, UNITS_TO_ADD, expiry_str, row['user_usage_id']))
    return False


def _upsert_tracking(cur, orcid_id, reissue_str):
    """orcid_id is UNIQUE, so this both creates and refreshes the tracking row."""
    cur.execute("""
        INSERT INTO OrcidCreditTracking (orcid_id, credit_reissue_date)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE credit_reissue_date = VALUES(credit_reissue_date)
    """, (orcid_id, reissue_str))


def process_one(conn, cur, row, action, dry_run=False, send_email=True):
    """Apply the classified action. Returns True on success."""
    orcid_id = row['orcid_id']
    party_id = row['party_id']
    email = row['email'] or ''
    username = row['username'] or ''
    total_before = row['total_units'] or 0
    remaining_before = row['remaining_units'] or 0

    now = datetime.now()
    reissue_str = (now + timedelta(days=REPLENISH_DAYS)).strftime('%Y-%m-%d %H:%M:%S')

    if dry_run:
        if action == ACTION_REPAIR:
            log("  [dry run][repair] orcid=%s party_id=%s -> would create tracking row only (free units still active until %s), NO units, no email"
                % (orcid_id, party_id, row['free_expiry_date']))
        elif action == ACTION_ENROLL:
            extra = " (new bucket)" if row['user_usage_id'] is None else ""
            log("  [dry run][enroll] orcid=%s party_id=%s email=%s -> would add %s units + create tracking row%s, no email"
                % (orcid_id, party_id, email or '(none)', UNITS_TO_ADD, extra))
        else:
            log("  [dry run][replenish] orcid=%s party_id=%s email=%s -> would add %s units, email"
                % (orcid_id, party_id, email or '(none)', UNITS_TO_ADD))
        return True

    try:
        if action == ACTION_REPAIR:
            # Units already granted; only the tracking row is missing. Align the
            # reissue date to the units the account actually holds so it is not
            # credited again early and is picked up when those units expire.
            existing_expiry = row['free_expiry_date'].strftime('%Y-%m-%d %H:%M:%S')
            _upsert_tracking(cur, orcid_id, existing_expiry)
            conn.commit()
            log("  [repair] orcid=%s party_id=%s tracking row created, reissue=%s, no units granted"
                % (orcid_id, party_id, existing_expiry))
            return True

        created_bucket = _add_units(cur, row, reissue_str)
        _upsert_tracking(cur, orcid_id, reissue_str)
        conn.commit()

        if action == ACTION_ENROLL:
            # First-time grant: no user email on purpose (the replenishment wording
            # does not apply). Reported to the admin instead. (TAIR3-890)
            log("  [enroll] orcid=%s party_id=%s total=%s->%s remaining=%s->%s%s email=none (first-time grant)"
                % (orcid_id, party_id, total_before, total_before + UNITS_TO_ADD,
                   remaining_before, remaining_before + UNITS_TO_ADD,
                   ' [new bucket]' if created_bucket else ''))
            return True

        send_ok = send_notification_email(email, username) if send_email else False
        email_status = 'sent' if send_ok else ('skipped (no Django)' if not send_email else 'skip/fail')
        log("  [replenish] orcid=%s party_id=%s total=%s->%s remaining=%s->%s email=%s"
            % (orcid_id, party_id, total_before, total_before + UNITS_TO_ADD,
               remaining_before, remaining_before + UNITS_TO_ADD, email_status))
        return True
    except Exception as e:
        conn.rollback()
        log("  [error][%s] orcid=%s party_id=%s: %s" % (action, orcid_id, party_id, e))
        return False


def send_crash_email(exc_text):
    """The run aborted before finishing - e.g. the DB was unreachable.

    Without this an outage is completely silent: no report (nothing was processed)
    and no history line beyond the CRASH marker. Best-effort; if Django itself is
    what failed to load, there is nothing to send with and the log is all we have.
    """
    try:
        from django.core.mail import send_mail
        today = datetime.now().strftime('%Y-%m-%d')
        send_mail(
            subject="[ORCID CREDITS] FAILED %s - run did not complete" % today,
            message=("The nightly ORCID credit run aborted with an unhandled error.\n"
                     "Accounts due for replenishment on this run were NOT processed.\n\n"
                     "%s\n"
                     "Full log: /var/log/api/orcid_replenish.log\n"
                     "Run history: %s\n" % (exc_text, HISTORY_FILE)),
            from_email=EMAIL_FROM,
            recipient_list=[REPORT_RECIPIENT],
            fail_silently=False,
        )
    except Exception as e:
        log("[crash email error] %s" % e)


def run():
    dry_run = '--dry-run' in sys.argv
    # TAIR3-890 self-heal runs by default so failed grants are corrected within a
    # day; --no-heal restricts the run to plain replenishment.
    heal = '--no-heal' not in sys.argv
    orcid_filter = None
    if '--orcid' in sys.argv:
        i = sys.argv.index('--orcid')
        if i + 1 < len(sys.argv):
            orcid_filter = sys.argv[i + 1].strip()

    settings = bootstrap_django()
    send_email = not dry_run
    db = settings.DATABASES['default']
    conn_kwargs = {
        'host': db.get('HOST') or 'localhost',
        'user': db.get('USER', ''),
        'passwd': db.get('PASSWORD', ''),
        'db': db.get('NAME', ''),
    }
    if db.get('PORT'):
        conn_kwargs['port'] = int(db['PORT'])

    conn = MySQLdb.connect(
        **conn_kwargs
    )
    cur = conn.cursor(MySQLdb.cursors.DictCursor)

    log("Mode: %s%s" % ("replenish + self-heal" if heal else "replenish only (--no-heal)",
                        " (dry run)" if dry_run else ""))
    eligible = fetch_eligible(cur, orcid_id=orcid_filter, heal=heal)

    if not eligible:
        log("Replenish ORCID credits: 0 eligible, 0 ok, 0 failed" + (" (dry run)" if dry_run else ""))
        # Nothing due tonight is a perfectly healthy outcome - publish RunSuccess=1
        # so the alarm sees the job ran, and send no email.
        if not dry_run:
            publish_run('OK', 1, 0, 0, 0, 0, 0, 0, note='nothing due')
        cur.close()
        conn.close()
        return

    ok = 0
    fail = 0
    now = datetime.now()
    by_action = {ACTION_REPLENISH: [], ACTION_ENROLL: [], ACTION_REPAIR: []}
    seen_orcids = set()

    for row in eligible:
        # An ORCID can appear on more than one TAIR credential; only act once per
        # ORCID per run so the same grant is not applied twice.
        if row['orcid_id'] in seen_orcids:
            log("  [skip] orcid=%s already processed this run (duplicate credential)" % row['orcid_id'])
            continue
        action = classify(row, now)
        if action != ACTION_REPLENISH and not heal:
            # Belt and braces: without --heal we never grant to a new account.
            log("  [skip] orcid=%s needs %s but self-heal is disabled (--no-heal)" % (row['orcid_id'], action))
            continue
        if process_one(conn, cur, row, action, dry_run=dry_run, send_email=send_email):
            ok += 1
            seen_orcids.add(row['orcid_id'])
            by_action[action].append({'orcid_id': row['orcid_id'], 'email': row['email'] or ''})
        else:
            fail += 1

    issue = run_has_issue(fail, by_action[ACTION_ENROLL], by_action[ACTION_REPAIR])

    if send_email and issue:
        send_report_email(by_action[ACTION_REPLENISH], by_action[ACTION_ENROLL],
                          by_action[ACTION_REPAIR], fail=fail)
    elif send_email:
        log("No issues this run - admin report email suppressed (history only).")

    if not dry_run:
        # RunSuccess=1 whenever the job completed its pass, even if individual
        # accounts failed - per-account failures are the email's job, not the
        # "did this job stop running" alarm's.
        publish_run(
            'ISSUE' if issue else 'OK', 1,
            len(eligible), ok, fail,
            len(by_action[ACTION_REPLENISH]), len(by_action[ACTION_ENROLL]),
            len(by_action[ACTION_REPAIR]),
            note='admin emailed' if issue else '')

    log("Replenish ORCID credits: %d eligible, %d ok, %d failed "
        "(replenished=%d, first-time enrolled=%d, tracking repaired=%d)%s"
        % (len(eligible), ok, fail,
           len(by_action[ACTION_REPLENISH]), len(by_action[ACTION_ENROLL]), len(by_action[ACTION_REPAIR]),
           " (dry run)" if dry_run else ""))
    cur.close()
    conn.close()
    if fail > 0:
        sys.exit(1)


def main():
    try:
        run()
    except SystemExit:
        raise
    except Exception:
        import traceback
        tb = traceback.format_exc()
        log("[fatal] run aborted:\n%s" % tb)
        publish_run('CRASH', 0, 0, 0, 0, 0, 0, 0, note='unhandled error - see log')
        if '--dry-run' not in sys.argv:
            send_crash_email(tb)
        sys.exit(1)


if __name__ == '__main__':
    main()
