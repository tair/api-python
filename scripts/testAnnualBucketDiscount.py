#!/usr/bin/python
import os
import sys
import time
from datetime import timedelta

import django
from django.utils import timezone


# Test script for annual reset of discounted TAIR 300-unit bucket purchase.
#
# Validates current behavior in BucketTypeCRUD:
# - No qualifying purchase in last 365 days => discounted first purchase price shown
# - Qualifying purchase within last 365 days => discount removed
# - Purchase older than 365 days => discount shown again

TEST_ORCID = "test-annual-discount-%d-%d" % (int(time.time()), os.getpid())
TARGET_BUCKET_TYPE_ID = 10  # 300-unit TAIR bucket

passed = 0
failed = 0


def bootstrap_django():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
    django.setup()


def assert_test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS: %s" % name)
    else:
        failed += 1
        print("  FAIL: %s -- %s" % (name, detail))


def get_bucket_discount(orcid_id):
    from partner.views import BucketTypeCRUD
    from rest_framework.test import APIRequestFactory

    factory = APIRequestFactory()
    request = factory.get('/partners/bucketTypes/', {'orcid_id': orcid_id})
    response = BucketTypeCRUD.as_view()(request)

    if response.status_code != 200:
        raise RuntimeError("BucketTypeCRUD returned status %s with body %s" % (response.status_code, response.data))

    for row in response.data:
        if row.get('bucketTypeId') == TARGET_BUCKET_TYPE_ID:
            return row.get('discountPercentage')
    raise RuntimeError("bucketTypeId=%s not found in response" % TARGET_BUCKET_TYPE_ID)


def create_bucket_transaction(orcid_id, when_dt):
    from subscription.models import BucketTransaction

    tx = BucketTransaction()
    tx.transaction_date = when_dt
    tx.bucket_type_id = TARGET_BUCKET_TYPE_ID
    tx.activation_code_id = int(time.time() * 1000000) % 2000000000
    tx.units_per_bucket = 300
    tx.transaction_type = 'create_bucket'
    tx.email_buyer = 'test@example.com'
    tx.institute_buyer = 'Test Institute'
    tx.orcid_id = orcid_id
    tx.save()
    return tx.bucket_transaction_id


def cleanup_test_rows():
    from subscription.models import BucketTransaction
    BucketTransaction.objects.filter(orcid_id=TEST_ORCID, bucket_type_id=TARGET_BUCKET_TYPE_ID).delete()


def main():
    bootstrap_django()
    from django.conf import settings
    from partner.models import BucketType

    print("=" * 60)
    print("Annual Bucket Discount Test")
    print("DB host: %s | DB name: %s" % (settings.DATABASES['default'].get('HOST'), settings.DATABASES['default'].get('NAME')))
    print("Test ORCID: %s" % TEST_ORCID)
    print("=" * 60)

    try:
        base_discount = BucketType.objects.get(bucketTypeId=TARGET_BUCKET_TYPE_ID).discountPercentage
    except Exception as e:
        print("Unable to read BucketType %s: %s" % (TARGET_BUCKET_TYPE_ID, e))
        sys.exit(1)

    try:
        cleanup_test_rows()

        print("\nTest 1: No purchases in last 365 days => discounted price available")
        discount = get_bucket_discount(TEST_ORCID)
        assert_test("Discount equals configured value", discount == base_discount, "got %s expected %s" % (discount, base_discount))

        print("\nTest 2: Recent purchase (<365 days) => discount removed")
        create_bucket_transaction(TEST_ORCID, timezone.now() - timedelta(days=200))
        discount = get_bucket_discount(TEST_ORCID)
        assert_test("Discount is zero after recent purchase", discount == 0, "got %s" % discount)

        print("\nTest 3: Purchase older than 365 days => discount available again")
        cleanup_test_rows()
        create_bucket_transaction(TEST_ORCID, timezone.now() - timedelta(days=366))
        discount = get_bucket_discount(TEST_ORCID)
        assert_test("Discount returns for new annual cycle", discount == base_discount, "got %s expected %s" % (discount, base_discount))

    finally:
        cleanup_test_rows()

    print("\n" + "=" * 60)
    print("Results: %d passed, %d failed" % (passed, failed))
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
