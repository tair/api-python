#!/usr/bin/python
"""
TAIR3-633: Daily cron to replenish 50 free usage units for eligible ORCID-linked TAIR accounts.

Eligibility:
- ORCID still linked (OrcidCredentials.orcid_id IS NOT NULL)
- TAIR credential (Credential.partnerId = 'tair')
- Has UserBucketUsage row
- In OrcidCreditTracking with credit_reissue_date <= today (reissue date has passed)

For each eligible account:
- Add 50 to total_units and remaining_units
- Set free_expiry_date = today + 1 year
- Set OrcidCreditTracking.credit_reissue_date = today + 1 year
- Send notification email (via Django send_mail, same as rest of repo)

Usage:
  python scripts/replenishOrcidCredits.py dev
  python scripts/replenishOrcidCredits.py prod [--dry-run]
  python scripts/replenishOrcidCredits.py dev --orcid 0009-0000-0624-7467   # single ORCID only

Run once per day via cron, e.g.:
  0 3 * * * cd /var/www/api-python && python scripts/replenishOrcidCredits.py prod >> /var/log/api/orcid_replenish.log 2>&1
"""
import MySQLdb
import os
import sys
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
ENVS = ['dev', 'uat', 'prod']
UNITS_TO_ADD = 50
REPLENISH_DAYS = 365

EMAIL_SUBJECT = "Your annual complimentary TAIR usage units have been replenished"
EMAIL_FROM = "info@phoenixbioinformatics.org"
EMAIL_BODY_TEMPLATE = """Hello,

Your annual complimentary TAIR usage units have been replenished.

50 usage units have been added to your account. These units are replenished once per year while your ORCID remains connected to your TAIR account.

If you have any questions, please contact us.

The TAIR Team
"""

# -----------------------------------------------------------------------------
# .env loading
# -----------------------------------------------------------------------------
def load_env():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    if not os.path.exists(env_path):
        print("Error: .env not found at %s" % env_path)
        sys.exit(1)
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, _, value = line.partition('=')
            os.environ[key.strip()] = value.strip()


def get_db_config(env):
    prefix = env.upper()
    return {
        'host': os.environ.get(prefix + '_DB_HOST', ''),
        'user': os.environ.get(prefix + '_DB_USER', ''),
        'password': os.environ.get(prefix + '_DB_PASSWORD', ''),
        'db': os.environ.get(prefix + '_DB_NAME', ''),
    }


def bootstrap_django():
    """Load Django so we can use send_mail (uses EMAIL_* from paywall2.settings). Returns True if ready to send email."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
        import django
        django.setup()
        return True
    except Exception as e:
        print("Warning: Django not available (%s). DB updates will run; email will be skipped." % e)
        return False


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
JOIN UserBucketUsage u ON c.partyId = u.partyId_id
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
        print("  [skip email] No email for user %s" % username)
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
        print("  [email error] %s: %s" % (to_email, e))
        return False


def replenish_one(conn, cur, row, dry_run=False, send_email=True):
    orcid_id = row['orcid_id']
    party_id = row['party_id']
    email = row['email'] or ''
    username = row['username'] or ''
    user_usage_id = row['user_usage_id']
    total_before = row['total_units']
    remaining_before = row['remaining_units']

    if dry_run:
        print("  [dry run] orcid=%s party_id=%s email=%s -> would add %s units" % (orcid_id, party_id, email or '(none)', UNITS_TO_ADD))
        return True

    reissue_date = datetime.now() + timedelta(days=REPLENISH_DAYS)
    reissue_str = reissue_date.strftime('%Y-%m-%d %H:%M:%S')

    try:
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
        print("  orcid=%s party_id=%s total=%s->%s remaining=%s->%s email=%s"
              % (orcid_id, party_id, total_before, total_before + UNITS_TO_ADD,
                 remaining_before, remaining_before + UNITS_TO_ADD, email_status))
        return True
    except Exception as e:
        conn.rollback()
        print("  [error] orcid=%s party_id=%s: %s" % (orcid_id, party_id, e))
        return False


def main():
    args = [a for a in sys.argv[1:] if a in ENVS]
    if len(args) < 1:
        print("Usage: python replenishOrcidCredits.py <dev|uat|prod> [--dry-run] [--orcid ORCID_ID]")
        sys.exit(1)

    env = args[0]
    dry_run = '--dry-run' in sys.argv
    orcid_filter = None
    if '--orcid' in sys.argv:
        i = sys.argv.index('--orcid')
        if i + 1 < len(sys.argv):
            orcid_filter = sys.argv[i + 1].strip()

    load_env()
    send_email = False
    if not dry_run:
        send_email = bootstrap_django()
    db_config = get_db_config(env)
    if not db_config['host']:
        print("Error: %s DB not configured in .env (%s_DB_HOST)" % (env, env.upper()))
        sys.exit(1)

    conn = MySQLdb.connect(
        host=db_config['host'],
        user=db_config['user'],
        passwd=db_config['password'],
        db=db_config['db'],
    )
    cur = conn.cursor(MySQLdb.cursors.DictCursor)

    print("Replenish ORCID credits [%s] %s" % (env, "(dry run)" if dry_run else ""))
    if orcid_filter:
        print("Filtering by ORCID: %s" % orcid_filter)
    print("Querying eligible accounts...")
    eligible = fetch_eligible(cur, orcid_id=orcid_filter)
    print("Found %d eligible account(s)." % len(eligible))

    if not eligible:
        cur.close()
        conn.close()
        return

    ok = 0
    fail = 0
    for row in eligible:
        if replenish_one(conn, cur, row, dry_run=dry_run, send_email=send_email):
            ok += 1
        else:
            fail += 1

    print("Done: %d ok, %d failed." % (ok, fail))
    cur.close()
    conn.close()
    if fail > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
