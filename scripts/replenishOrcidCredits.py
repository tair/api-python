#!/usr/bin/python
"""
TAIR3-633: Daily cron to replenish 50 free usage units for eligible ORCID-linked TAIR accounts.

Eligibility:
- ORCID still linked (OrcidCredentials.orcid_id IS NOT NULL)
- TAIR credential (Credential.partnerId = 'tair')
- In OrcidCreditTracking with credit_reissue_date <= today (reissue date has passed)
- UserBucketUsage row is optional; one is created if missing (e.g. ORCID moved to a new account)

For each eligible account:
- Add 50 to total_units and remaining_units
- Set free_expiry_date = today + 1 year
- Set OrcidCreditTracking.credit_reissue_date = today + 1 year
- Send notification email (via Django send_mail, same as rest of repo)

Usage:
  python scripts/replenishOrcidCredits.py
  python scripts/replenishOrcidCredits.py --dry-run
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
    t.credit_reissue_date
FROM OrcidCredentials o
JOIN Credential c ON o.CredentialId = c.id
LEFT JOIN UserBucketUsage u ON c.partyId = u.partyId_id
JOIN OrcidCreditTracking t ON o.orcid_id = t.orcid_id
WHERE o.orcid_id IS NOT NULL
  AND o.orcid_id != ''
  AND c.partnerId = 'tair'
  AND t.credit_reissue_date IS NOT NULL
  AND t.credit_reissue_date <= NOW()
ORDER BY o.orcid_id
"""


def fetch_eligible(cur, orcid_id=None):
    if orcid_id:
        q = ELIGIBLE_QUERY.replace("ORDER BY o.orcid_id", "AND o.orcid_id = %s\nORDER BY o.orcid_id")
        cur.execute(q, (orcid_id,))
    else:
        cur.execute(ELIGIBLE_QUERY)
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


def send_report_email(replenished_list):
    """Send a summary report of all replenished accounts to the admin."""
    if not replenished_list:
        return
    try:
        from django.core.mail import send_mail
        today = datetime.now().strftime('%Y-%m-%d')
        lines = ["ORCID ID | Email"]
        lines.append("-" * 50)
        for entry in replenished_list:
            lines.append("%s | %s" % (entry['orcid_id'], entry['email'] or '(none)'))

        body = "ORCID credit replenishment report for %s\n\n" % today
        body += "Total replenished: %d\n\n" % len(replenished_list)
        body += "\n".join(lines) + "\n"

        send_mail(
            subject="ORCID Credit Replenishment Report - %s" % today,
            message=body,
            from_email=EMAIL_FROM,
            recipient_list=[REPORT_RECIPIENT],
            fail_silently=False,
        )
    except Exception as e:
        log("[report email error] %s" % e)


def replenish_one(conn, cur, row, dry_run=False, send_email=True):
    orcid_id = row['orcid_id']
    party_id = row['party_id']
    email = row['email'] or ''
    username = row['username'] or ''
    user_usage_id = row['user_usage_id']
    total_before = row['total_units'] or 0
    remaining_before = row['remaining_units'] or 0
    needs_bucket = user_usage_id is None

    if dry_run:
        extra = " (new bucket)" if needs_bucket else ""
        log("  [dry run] orcid=%s party_id=%s email=%s -> would add %s units%s" % (orcid_id, party_id, email or '(none)', UNITS_TO_ADD, extra))
        return True

    reissue_date = datetime.now() + timedelta(days=REPLENISH_DAYS)
    reissue_str = reissue_date.strftime('%Y-%m-%d %H:%M:%S')

    try:
        if needs_bucket:
            cur.execute("""
                INSERT INTO UserBucketUsage (partyId_id, partner_id, total_units, remaining_units, free_expiry_date)
                VALUES (%s, 'tair', %s, %s, %s)
            """, (party_id, UNITS_TO_ADD, UNITS_TO_ADD, reissue_str))
            log("  [new bucket] created UserBucketUsage for party_id=%s" % party_id)
        else:
            cur.execute("""
                UPDATE UserBucketUsage
                SET total_units = total_units + %s,
                    remaining_units = remaining_units + %s,
                    free_expiry_date = %s
                WHERE user_usage_id = %s
            """, (UNITS_TO_ADD, UNITS_TO_ADD, reissue_str, user_usage_id))

        cur.execute("""
            UPDATE OrcidCreditTracking
            SET credit_reissue_date = %s
            WHERE orcid_id = %s
        """, (reissue_str, orcid_id))

        conn.commit()

        send_ok = send_notification_email(email, username) if send_email else False
        email_status = 'sent' if send_ok else ('skipped (no Django)' if not send_email else 'skip/fail')
        log("  orcid=%s party_id=%s total=%s->%s remaining=%s->%s email=%s"
            % (orcid_id, party_id, total_before, total_before + UNITS_TO_ADD,
               remaining_before, remaining_before + UNITS_TO_ADD, email_status))
        return True
    except Exception as e:
        conn.rollback()
        log("  [error] orcid=%s party_id=%s: %s" % (orcid_id, party_id, e))
        return False


def main():
    dry_run = '--dry-run' in sys.argv
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

    eligible = fetch_eligible(cur, orcid_id=orcid_filter)

    if not eligible:
        log("Replenish ORCID credits: 0 eligible, 0 ok, 0 failed" + (" (dry run)" if dry_run else ""))
        cur.close()
        conn.close()
        return

    ok = 0
    fail = 0
    replenished = []
    for row in eligible:
        if replenish_one(conn, cur, row, dry_run=dry_run, send_email=send_email):
            ok += 1
            replenished.append({'orcid_id': row['orcid_id'], 'email': row['email'] or ''})
        else:
            fail += 1

    if replenished and send_email:
        send_report_email(replenished)

    log("Replenish ORCID credits: %d eligible, %d ok, %d failed" % (len(eligible), ok, fail))
    cur.close()
    conn.close()
    if fail > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
