#!/usr/bin/python
import MySQLdb
import os
import sys
import requests
import json
import time
import django
from django.conf import settings

# Test script for ORCID credit tracking fix (TAIR3-633)
#
# Tests the add_free endpoint against the dev API after deploying the fix.
# Sets up DB state for each scenario, calls the API, checks the response.
#
# Usage:
#   python testOrcidCreditTracking.py
#   python testOrcidCreditTracking.py http://your-api-base
#
# Prerequisites:
#   - Run from an API instance with project settings configured
#   - pip install requests mysqlclient

DEFAULT_API_BASE = "http://127.0.0.1"
ADD_FREE_URL = DEFAULT_API_BASE + "/subscriptions/add_free"

# We use swapp19902222 (partyId 164496) as Account A
# and tberardini (partyId 26629) as Account B
# Both have ORCID linked and expired free_expiry_date on dev
ACCOUNT_A_PARTY_ID = "164496"
ACCOUNT_A_CREDENTIAL_ID = 163142
ACCOUNT_B_PARTY_ID = "26629"
ACCOUNT_B_CREDENTIAL_ID = 26629  # based on earlier query: credentialId matches
# Use a run-unique ORCID value to avoid collisions with existing credentials.
TEST_ORCID = "test-orcid-%d-%d" % (int(time.time()), os.getpid())

passed = 0
failed = 0

def bootstrap_django():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
    django.setup()

def get_db():
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
    return conn, conn.cursor()

def refresh_db_view(conn):
    """
    End current transaction so subsequent reads can see updates committed by
    the API request (which runs in a separate DB connection/process).
    """
    conn.commit()

def call_add_free(party_id):
    """Call PUT /subscriptions/add_free and return (status_code, response_json)"""
    resp = requests.put(ADD_FREE_URL, json={"partyId": party_id})
    try:
        body = resp.json()
    except:
        body = resp.text
    return resp.status_code, body

def assert_test(test_name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS: %s" % test_name)
    else:
        failed += 1
        print("  FAIL: %s -- %s" % (test_name, detail))

def save_state(conn, cur):
    """Save original state of rows we'll modify so we can restore them."""
    state = {}

    cur.execute("SELECT orcid_id FROM OrcidCredentials WHERE CredentialId = %s", (ACCOUNT_A_CREDENTIAL_ID,))
    row = cur.fetchone()
    state['account_a_orcid_id'] = row[0] if row else None

    cur.execute("SELECT orcid_id FROM OrcidCredentials WHERE CredentialId = %s", (ACCOUNT_B_CREDENTIAL_ID,))
    row = cur.fetchone()
    state['account_b_orcid_id'] = row[0] if row else None

    cur.execute("SELECT total_units, remaining_units, free_expiry_date FROM UserBucketUsage WHERE partyId_id = %s", (ACCOUNT_A_PARTY_ID,))
    row = cur.fetchone()
    state['account_a_bucket'] = row

    cur.execute("SELECT total_units, remaining_units, free_expiry_date FROM UserBucketUsage WHERE partyId_id = %s", (ACCOUNT_B_PARTY_ID,))
    row = cur.fetchone()
    state['account_b_bucket'] = row

    cur.execute("SELECT orcid_id, credit_reissue_date FROM OrcidCreditTracking WHERE orcid_id = %s", (TEST_ORCID,))
    row = cur.fetchone()
    state['tracking'] = row

    return state

def restore_state(conn, cur, state):
    """Restore DB to original state."""
    # Clear both first to avoid unique key collisions when moving an ORCID
    # value back between credentials during restore.
    cur.execute("UPDATE OrcidCredentials SET orcid_id = NULL WHERE CredentialId IN (%s, %s)",
                (ACCOUNT_A_CREDENTIAL_ID, ACCOUNT_B_CREDENTIAL_ID))
    cur.execute("UPDATE OrcidCredentials SET orcid_id = %s WHERE CredentialId = %s",
                (state['account_a_orcid_id'], ACCOUNT_A_CREDENTIAL_ID))
    cur.execute("UPDATE OrcidCredentials SET orcid_id = %s WHERE CredentialId = %s",
                (state['account_b_orcid_id'], ACCOUNT_B_CREDENTIAL_ID))

    if state['account_a_bucket']:
        cur.execute("UPDATE UserBucketUsage SET total_units=%s, remaining_units=%s, free_expiry_date=%s WHERE partyId_id=%s",
                    (state['account_a_bucket'][0], state['account_a_bucket'][1], state['account_a_bucket'][2], ACCOUNT_A_PARTY_ID))

    if state['account_b_bucket']:
        cur.execute("UPDATE UserBucketUsage SET total_units=%s, remaining_units=%s, free_expiry_date=%s WHERE partyId_id=%s",
                    (state['account_b_bucket'][0], state['account_b_bucket'][1], state['account_b_bucket'][2], ACCOUNT_B_PARTY_ID))

    if state['tracking']:
        cur.execute("UPDATE OrcidCreditTracking SET credit_reissue_date = %s WHERE orcid_id = %s",
                    (state['tracking'][1], TEST_ORCID))
    else:
        cur.execute("DELETE FROM OrcidCreditTracking WHERE orcid_id = %s", (TEST_ORCID,))

    conn.commit()


def test_1_no_orcid_linked(conn, cur):
    """add_free on an account with no ORCID linked should return 400."""
    print("\nTest 1: No ORCID linked")

    cur.execute("UPDATE OrcidCredentials SET orcid_id = NULL WHERE CredentialId = %s", (ACCOUNT_A_CREDENTIAL_ID,))
    cur.execute("DELETE FROM OrcidCreditTracking WHERE orcid_id = %s", (TEST_ORCID,))
    conn.commit()

    status_code, body = call_add_free(ACCOUNT_A_PARTY_ID)
    assert_test("Returns 400", status_code == 400, "got %s" % status_code)
    assert_test("Error mentions ORCID", "ORCID must be linked" in str(body), body)


def test_2_first_time_credits(conn, cur):
    """ORCID linked, no tracking row, expired bucket -> should grant 50 credits."""
    print("\nTest 2: First-time credits (ORCID linked, no tracking row)")

    cur.execute("UPDATE OrcidCredentials SET orcid_id = %s WHERE CredentialId = %s", (TEST_ORCID, ACCOUNT_A_CREDENTIAL_ID))
    cur.execute("DELETE FROM OrcidCreditTracking WHERE orcid_id = %s", (TEST_ORCID,))
    cur.execute("UPDATE UserBucketUsage SET free_expiry_date = '2020-01-01' WHERE partyId_id = %s", (ACCOUNT_A_PARTY_ID,))
    conn.commit()

    cur.execute("SELECT remaining_units FROM UserBucketUsage WHERE partyId_id = %s", (ACCOUNT_A_PARTY_ID,))
    before_units = cur.fetchone()[0]

    status_code, body = call_add_free(ACCOUNT_A_PARTY_ID)
    assert_test("Returns 201", status_code == 201, "got %s: %s" % (status_code, body))
    refresh_db_view(conn)

    cur.execute("SELECT remaining_units FROM UserBucketUsage WHERE partyId_id = %s", (ACCOUNT_A_PARTY_ID,))
    after_units = cur.fetchone()[0]
    assert_test("Credits increased by 50", after_units == before_units + 50,
                "before=%s after=%s" % (before_units, after_units))

    cur.execute("SELECT credit_reissue_date FROM OrcidCreditTracking WHERE orcid_id = %s", (TEST_ORCID,))
    row = cur.fetchone()
    assert_test("OrcidCreditTracking row created", row is not None, "no row found")


def test_3_same_account_double_claim(conn, cur):
    """Calling add_free twice on the same account should be blocked the second time."""
    print("\nTest 3: Same account, call add_free again (credits still active)")

    status_code, body = call_add_free(ACCOUNT_A_PARTY_ID)
    assert_test("Returns 400", status_code == 400, "got %s: %s" % (status_code, body))
    assert_test("Error mentions expired", "cannot be added until previous units expired" in str(body), body)


def test_4_cross_account_exploit(conn, cur):
    """Unlink ORCID from A, link to B, try add_free on B -> should be blocked by OrcidCreditTracking."""
    print("\nTest 4: Cross-account exploit (unlink from A, link to B)")

    cur.execute("UPDATE OrcidCredentials SET orcid_id = NULL WHERE CredentialId = %s", (ACCOUNT_A_CREDENTIAL_ID,))
    cur.execute("UPDATE OrcidCredentials SET orcid_id = %s WHERE CredentialId = %s", (TEST_ORCID, ACCOUNT_B_CREDENTIAL_ID))
    cur.execute("UPDATE UserBucketUsage SET free_expiry_date = '2020-01-01' WHERE partyId_id = %s", (ACCOUNT_B_PARTY_ID,))
    conn.commit()

    status_code, body = call_add_free(ACCOUNT_B_PARTY_ID)
    assert_test("Returns 400", status_code == 400, "got %s: %s" % (status_code, body))
    assert_test("Error mentions expired", "cannot be added until previous units expired" in str(body), body)


def test_5_tracking_expired_allows_grant(conn, cur):
    """If credit_reissue_date is in the past, the same ORCID should get credits again."""
    print("\nTest 5: Tracking expired -> should allow credits")

    cur.execute("UPDATE OrcidCredentials SET orcid_id = NULL WHERE CredentialId = %s", (ACCOUNT_B_CREDENTIAL_ID,))
    cur.execute("UPDATE OrcidCredentials SET orcid_id = %s WHERE CredentialId = %s", (TEST_ORCID, ACCOUNT_A_CREDENTIAL_ID))
    cur.execute("UPDATE OrcidCreditTracking SET credit_reissue_date = '2020-01-01' WHERE orcid_id = %s", (TEST_ORCID,))
    cur.execute("UPDATE UserBucketUsage SET free_expiry_date = '2020-01-01' WHERE partyId_id = %s", (ACCOUNT_A_PARTY_ID,))
    conn.commit()

    status_code, body = call_add_free(ACCOUNT_A_PARTY_ID)
    assert_test("Returns 201", status_code == 201, "got %s: %s" % (status_code, body))
    refresh_db_view(conn)

    cur.execute("SELECT credit_reissue_date FROM OrcidCreditTracking WHERE orcid_id = %s", (TEST_ORCID,))
    row = cur.fetchone()
    assert_test("Tracking date updated", row is not None and row[0].year >= 2026,
                "date=%s" % (row[0] if row else None))


def test_6_cross_account_after_expiry(conn, cur):
    """After tracking expires, ORCID on a new account should get credits."""
    print("\nTest 6: Cross-account after tracking expired")

    cur.execute("UPDATE OrcidCredentials SET orcid_id = NULL WHERE CredentialId = %s", (ACCOUNT_A_CREDENTIAL_ID,))
    cur.execute("UPDATE OrcidCredentials SET orcid_id = %s WHERE CredentialId = %s", (TEST_ORCID, ACCOUNT_B_CREDENTIAL_ID))
    cur.execute("UPDATE OrcidCreditTracking SET credit_reissue_date = '2020-01-01' WHERE orcid_id = %s", (TEST_ORCID,))
    cur.execute("UPDATE UserBucketUsage SET free_expiry_date = '2020-01-01' WHERE partyId_id = %s", (ACCOUNT_B_PARTY_ID,))
    conn.commit()

    cur.execute("SELECT remaining_units FROM UserBucketUsage WHERE partyId_id = %s", (ACCOUNT_B_PARTY_ID,))
    before_units = cur.fetchone()[0]

    status_code, body = call_add_free(ACCOUNT_B_PARTY_ID)
    assert_test("Returns 201", status_code == 201, "got %s: %s" % (status_code, body))
    refresh_db_view(conn)

    cur.execute("SELECT remaining_units FROM UserBucketUsage WHERE partyId_id = %s", (ACCOUNT_B_PARTY_ID,))
    after_units = cur.fetchone()[0]
    assert_test("Credits increased by 50", after_units == before_units + 50,
                "before=%s after=%s" % (before_units, after_units))


def main():
    global passed, failed
    global ADD_FREE_URL

    api_base = DEFAULT_API_BASE
    if len(sys.argv) > 1:
        api_base = sys.argv[1].strip()
    api_base = api_base.rstrip('/')
    ADD_FREE_URL = api_base + "/subscriptions/add_free"

    bootstrap_django()
    conn, cur = get_db()

    print("Saving original DB state...")
    state = save_state(conn, cur)

    print("=" * 60)
    print("ORCID Credit Tracking - Edge Case Tests")
    print("API: %s" % ADD_FREE_URL)
    print("=" * 60)

    try:
        test_1_no_orcid_linked(conn, cur)
        test_2_first_time_credits(conn, cur)
        test_3_same_account_double_claim(conn, cur)
        test_4_cross_account_exploit(conn, cur)
        test_5_tracking_expired_allows_grant(conn, cur)
        test_6_cross_account_after_expiry(conn, cur)
    finally:
        print("\nRestoring original DB state...")
        restore_state(conn, cur, state)
        cur.close()
        conn.close()

    print("\n" + "=" * 60)
    print("Results: %d passed, %d failed" % (passed, failed))
    print("=" * 60)

    if failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
