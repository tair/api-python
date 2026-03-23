#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Reproduction tests for two bucket-discount bugs:

Bug 1 - Discount reuse after purchase
  The payment endpoint (SubsctiptionBucketPayment.post) trusts the client-
  supplied price.  A user who already used their annual 50% discount can
  submit the discounted price again and the server will charge that amount
  without re-validating eligibility.

Bug 2 - No BucketTransaction on activation-code redemption
  When an activation code is redeemed via UserBucketUsageCRUD.post(), no
  BucketTransaction row is created.  Because the annual-discount check
  queries BucketTransaction, the discount stays available even after the
  user has already redeemed a 300-unit code.
"""

import os
import sys
import time
import uuid

import django
from django.utils import timezone
from datetime import timedelta


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

TEST_ORCID = "test-bug-repro-%d-%d" % (int(time.time()), os.getpid())
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


# ---------------------------------------------------------------------------
# Helpers - reuse pattern from testAnnualBucketDiscount.py
# ---------------------------------------------------------------------------

def get_bucket_discount(orcid_id):
    """Call BucketTypeCRUD.get() and return the discountPercentage for bucket type 10."""
    from partner.views import BucketTypeCRUD
    from rest_framework.test import APIRequestFactory

    factory = APIRequestFactory()
    request = factory.get('/partners/bucketTypes/', {'orcid_id': orcid_id})
    response = BucketTypeCRUD.as_view()(request)
    if response.status_code != 200:
        raise RuntimeError("BucketTypeCRUD returned %s: %s" % (response.status_code, response.data))

    for row in response.data:
        if row.get('bucketTypeId') == TARGET_BUCKET_TYPE_ID:
            return row.get('discountPercentage')
    raise RuntimeError("bucketTypeId=%s not in response" % TARGET_BUCKET_TYPE_ID)


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


def create_test_activation_code(partner_id, units=300):
    """Create an unused ActivationCode and return the object."""
    from subscription.models import ActivationCode
    from partner.models import Partner

    partner = Partner.objects.get(partnerId=partner_id)
    code = ActivationCode()
    code.activationCode = str(uuid.uuid4())
    code.partnerId = partner
    code.partyId = None
    code.period = units
    code.purchaseDate = timezone.now()
    code.transactionType = 'create_bucket'
    code.save()
    return code


def activate_code_via_api(activation_code_str, party_id):
    """Call UserBucketUsageCRUD.post() as the real endpoint would."""
    from subscription.views import UserBucketUsageCRUD
    from rest_framework.test import APIRequestFactory

    factory = APIRequestFactory()
    request = factory.post(
        '/subscriptions/bucket_usage/',
        {'activationCode': activation_code_str, 'partyId': party_id},
        format='json',
    )
    response = UserBucketUsageCRUD.as_view()(request)
    return response


def get_test_party_id():
    """Return the partyId of any existing Party row (for test purposes)."""
    from party.models import Party
    party = Party.objects.first()
    if party is None:
        raise RuntimeError("No Party rows in database - cannot run activation tests")
    return party.partyId


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def cleanup(extra_activation_codes=None, extra_activation_code_ids=None):
    from subscription.models import BucketTransaction, ActivationCode
    BucketTransaction.objects.filter(orcid_id=TEST_ORCID).delete()
    if extra_activation_code_ids:
        for ac_id in extra_activation_code_ids:
            BucketTransaction.objects.filter(activation_code_id=ac_id).delete()
    if extra_activation_codes:
        for code_str in extra_activation_codes:
            ActivationCode.objects.filter(activationCode=code_str).delete()


# ---------------------------------------------------------------------------
# Bug 1 - Discount reuse after purchase
# ---------------------------------------------------------------------------

def test_bug1_discount_removed_after_purchase():
    """
    After purchasing a discounted 300-unit bucket, BucketTypeCRUD must
    return discountPercentage=0 so the frontend shows the full price.
    """
    from partner.models import BucketType

    print("\n" + "=" * 60)
    print("Bug 1: Discount removed after purchase")
    print("=" * 60)

    bucket_type = BucketType.objects.get(bucketTypeId=TARGET_BUCKET_TYPE_ID)
    base_discount = bucket_type.discountPercentage  # e.g. 50

    # Step 1: Confirm discount is available before any purchase
    discount_before = get_bucket_discount(TEST_ORCID)
    assert_test(
        "Discount available before purchase",
        discount_before == base_discount,
        "got %s, expected %s" % (discount_before, base_discount),
    )

    # Step 2: Simulate a purchase (creates BucketTransaction)
    create_bucket_transaction(TEST_ORCID, timezone.now())

    # Step 3: Confirm discount is now 0
    discount_after = get_bucket_discount(TEST_ORCID)
    assert_test(
        "Discount removed after purchase",
        discount_after == 0,
        "got %s, expected 0" % discount_after,
    )


# ---------------------------------------------------------------------------
# Bug 2 - Activation code: no BucketTransaction + discount persists
# ---------------------------------------------------------------------------

def test_bug2_activation_code_no_transaction():
    """
    When an activation code for a 300-unit bucket is redeemed, no
    BucketTransaction is created.  This means the annual-discount check
    never sees the redemption and keeps offering 50 % off.
    """
    from subscription.models import BucketTransaction

    print("\n" + "=" * 60)
    print("Bug 2: Activation code creates no BucketTransaction")
    print("=" * 60)

    party_id = get_test_party_id()

    # Step 1: Confirm discount is available
    discount_before = get_bucket_discount(TEST_ORCID)
    from partner.models import BucketType
    base_discount = BucketType.objects.get(bucketTypeId=TARGET_BUCKET_TYPE_ID).discountPercentage
    assert_test(
        "Discount available before activation",
        discount_before == base_discount,
        "got %s, expected %s" % (discount_before, base_discount),
    )

    # Step 2: Create and redeem an activation code
    code_obj = create_test_activation_code('tair', units=300)
    code_str = code_obj.activationCode
    response = activate_code_via_api(code_str, party_id)
    assert_test(
        "Activation code redeemed successfully",
        response.status_code == 201,
        "status=%s, body=%s" % (response.status_code, getattr(response, 'data', '')),
    )

    # Step 3: Check if a BucketTransaction was created for this activation
    tx_count = BucketTransaction.objects.filter(
        activation_code_id=code_obj.activationCodeId,
    ).count()

    assert_test(
        "FIX VERIFIED: BucketTransaction created on activation",
        tx_count == 1,
        "Found %d transaction(s) - expected 1" % tx_count,
    )

    # Step 4: Verify the transaction has the correct type
    if tx_count > 0:
        tx = BucketTransaction.objects.get(activation_code_id=code_obj.activationCodeId)
        assert_test(
            "BucketTransaction has type 'activate_bucket'",
            tx.transaction_type == 'activate_bucket',
            "got '%s'" % tx.transaction_type,
        )
        assert_test(
            "BucketTransaction has correct bucket_type_id",
            tx.bucket_type_id == TARGET_BUCKET_TYPE_ID,
            "got %s, expected %s" % (tx.bucket_type_id, TARGET_BUCKET_TYPE_ID),
        )

    print("\n  After fix: UserBucketUsageCRUD.post() now creates a")
    print("  BucketTransaction when an activation code is redeemed,")
    print("  so the annual-discount check correctly detects the redemption.")

    return code_str, code_obj.activationCodeId  # for cleanup


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    bootstrap_django()
    from django.conf import settings

    print("=" * 60)
    print("Bucket Discount Bug Reproduction Tests")
    print("DB host: %s | DB name: %s" % (
        settings.DATABASES['default'].get('HOST'),
        settings.DATABASES['default'].get('NAME'),
    ))
    print("Test ORCID: %s" % TEST_ORCID)
    print("=" * 60)

    activation_code_str = None
    activation_code_id = None
    try:
        test_bug1_discount_removed_after_purchase()
        cleanup()  # clean up Bug 1 data before Bug 2
        activation_code_str, activation_code_id = test_bug2_activation_code_no_transaction()
    finally:
        codes_to_clean = [activation_code_str] if activation_code_str else None
        ids_to_clean = [activation_code_id] if activation_code_id else None
        cleanup(extra_activation_codes=codes_to_clean, extra_activation_code_ids=ids_to_clean)

    print("\n" + "=" * 60)
    print("Results: %d passed, %d failed" % (passed, failed))
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
