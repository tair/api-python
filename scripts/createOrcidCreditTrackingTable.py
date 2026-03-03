#!/usr/bin/python
import MySQLdb
import os
import sys

# Script to create the OrcidCreditTracking table and backfill it from
# OrcidCredentials + Credential + UserBucketUsage.
#
# Usage:
#   python createOrcidCreditTrackingTable.py dev
#   python createOrcidCreditTrackingTable.py uat
#   python createOrcidCreditTrackingTable.py prod

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        print("Error: .env file not found at %s" % env_path)
        sys.exit(1)
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, _, value = line.partition('=')
            os.environ[key.strip()] = value.strip()

load_env()

ENVS = ['dev', 'uat', 'prod']

def get_db_config(env):
    prefix = env.upper()
    return {
        'host': os.environ.get('%s_DB_HOST' % prefix, ''),
        'user': os.environ.get('%s_DB_USER' % prefix, ''),
        'password': os.environ.get('%s_DB_PASSWORD' % prefix, ''),
        'db': os.environ.get('%s_DB_NAME' % prefix, ''),
    }

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS OrcidCreditTracking (
    orcid_credit_tracking_id INT AUTO_INCREMENT PRIMARY KEY,
    orcid_id VARCHAR(255) NOT NULL UNIQUE,
    credit_reissue_date DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

BACKFILL_SQL = """
INSERT INTO OrcidCreditTracking (orcid_id, credit_reissue_date)
SELECT o.orcid_id, u.free_expiry_date
FROM OrcidCredentials o
JOIN Credential c ON o.CredentialId = c.id
JOIN UserBucketUsage u ON c.partyId = u.partyId_id
WHERE o.orcid_id IS NOT NULL
  AND u.free_expiry_date IS NOT NULL;
"""

COUNT_SQL = "SELECT COUNT(*) FROM OrcidCreditTracking;"

def connect(env):
    config = get_db_config(env)
    conn = MySQLdb.connect(
        host=config['host'],
        user=config['user'],
        passwd=config['password'],
        db=config['db'],
    )
    cur = conn.cursor()
    return conn, cur

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ENVS:
        print("Usage: python createOrcidCreditTrackingTable.py <dev|uat|prod>")
        sys.exit(1)

    env = sys.argv[1]
    print("Connecting to %s database..." % env)

    conn, cur = connect(env)

    print("Creating OrcidCreditTracking table...")
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    print("Table created (or already exists).")

    cur.execute(COUNT_SQL)
    existing_count = cur.fetchone()[0]
    if existing_count > 0:
        print("Table already has %d rows. Skipping backfill." % existing_count)
        print("To re-run backfill, TRUNCATE the table first.")
    else:
        print("Backfilling from OrcidCredentials + UserBucketUsage...")
        cur.execute(BACKFILL_SQL)
        conn.commit()
        print("Inserted %d rows." % cur.rowcount)

    cur.execute(COUNT_SQL)
    total = cur.fetchone()[0]
    print("OrcidCreditTracking now has %d total rows." % total)

    cur.close()
    conn.close()
    print("Done.")

if __name__ == '__main__':
    main()
