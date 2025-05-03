import requests
import json
import ipaddress
import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from django.utils import timezone
from paywall2.settings import BASF_GATEWAY_API_KEY, BASF_GATEWAY_API_URL
from party.models import IpRange
from common.common import is_valid_ip, ip2long
from django.db import transaction
from netaddr import IPNetwork, IPAddress, IPRange

def fetch_basf_ips():
    """Fetch IP addresses from BASF gateway API"""
    try:
        response = requests.get(
            BASF_GATEWAY_API_URL,
            params={'apikey': BASF_GATEWAY_API_KEY}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching IPs from BASF API: {}".format(e))
        return []

def cidr_to_range(cidr):
    """Convert CIDR notation to start and end IP addresses"""
    network = IPNetwork(cidr)
    return str(network[0]), str(network[-1])

def range_contains(range1_start, range1_end, range2_start, range2_end):
    """Check if range1 contains range2"""
    return range1_start <= range2_start and range1_end >= range2_end

def update_ip_ranges(party_id=30767):
    """Update IP ranges in database based on BASF list"""
    # Fetch current IPs from BASF
    basf_cidrs = fetch_basf_ips()
    if not basf_cidrs:
        print("No IPs fetched from BASF API")
        return

    # Get all IPs from database (both active and expired)
    all_db_ips = IpRange.objects.filter(partyId=party_id)
    active_ips = all_db_ips.filter(expiredAt=None)
    expired_ips = all_db_ips.filter(expiredAt__isnull=False)

    # Convert BASF CIDRs to ranges
    basf_ranges = []
    for cidr in basf_cidrs:
        try:
            start, end = cidr_to_range(cidr)
            basf_ranges.append({
                'start': start,
                'end': end,
                'start_long': ip2long(start),
                'end_long': ip2long(end)
            })
        except Exception as e:
            print("Error processing CIDR {}: {}".format(cidr, e))

    # Print current state
    print("\n=== Current Active IP Ranges in Database ===")
    for ip_range in active_ips:
        print("- {} - {}".format(ip_range.start, ip_range.end))

    print("\n=== Currently Expired IP Ranges in Database ===")
    for ip_range in expired_ips:
        print("- {} - {}".format(ip_range.start, ip_range.end))

    print("\n=== IP Ranges from BASF API ===")
    for range_info in basf_ranges:
        print("- {} - {}".format(range_info['start'], range_info['end']))

    # Analyze overlaps and changes needed
    ranges_to_expire = []
    ranges_to_add = []
    ranges_to_keep = []
    ranges_to_reactivate = []

    # First pass: Check if any BASF ranges are contained within existing active ranges
    for db_range in active_ips:
        # Check if this range contains any BASF range
        contains_basf = False
        for basf_range in basf_ranges:
            if range_contains(db_range.startLong, db_range.endLong, basf_range['start_long'], basf_range['end_long']):
                contains_basf = True
                ranges_to_keep.append({
                    'db_range': db_range,
                    'basf_range': basf_range,
                    'reason': 'contains BASF range'
                })
                break

        if not contains_basf:
            ranges_to_expire.append(db_range)

    # Second pass: Check if any BASF ranges are contained within existing expired ranges
    for db_range in expired_ips:
        # Check if this range contains any BASF range
        contains_basf = False
        for basf_range in basf_ranges:
            if range_contains(db_range.startLong, db_range.endLong, basf_range['start_long'], basf_range['end_long']):
                contains_basf = True
                ranges_to_reactivate.append({
                    'db_range': db_range,
                    'basf_range': basf_range,
                    'reason': 'contains BASF range'
                })
                break

    # Third pass: Check for new ranges to add
    for basf_range in basf_ranges:
        # Check if this BASF range is already covered by any database range
        covered = False
        for db_range in active_ips:
            if range_contains(db_range.startLong, db_range.endLong, basf_range['start_long'], basf_range['end_long']):
                covered = True
                break

        for db_range in expired_ips:
            if range_contains(db_range.startLong, db_range.endLong, basf_range['start_long'], basf_range['end_long']):
                covered = True
                break

        if not covered:
            ranges_to_add.append(basf_range)

    # Print analysis
    print("\n=== IP Ranges to be Expired ===")
    for ip_range in ranges_to_expire:
        print("- {} - {}".format(ip_range.start, ip_range.end))

    print("\n=== IP Ranges to be Reactivated ===")
    for range_info in ranges_to_reactivate:
        print("- {} - {}".format(range_info['db_range'].start, range_info['db_range'].end))

    print("\n=== IP Ranges to be Added ===")
    for range_info in ranges_to_add:
        print("- {} - {}".format(range_info['start'], range_info['end']))

    print("\n=== IP Ranges to be Kept ===")
    for range_info in ranges_to_keep:
        print("- {} - {} ({})".format(
            range_info['db_range'].start,
            range_info['db_range'].end,
            range_info['reason']
        ))

    # Print summary
    print("\n=== Summary ===")
    print("Total active IP ranges in database: {}".format(len(active_ips)))
    print("Total expired IP ranges in database: {}".format(len(expired_ips)))
    print("Total IP ranges from BASF API: {}".format(len(basf_ranges)))
    print("IP ranges to be expired: {}".format(len(ranges_to_expire)))
    print("IP ranges to be reactivated: {}".format(len(ranges_to_reactivate)))
    print("IP ranges to be added: {}".format(len(ranges_to_add)))
    print("IP ranges to be kept: {}".format(len(ranges_to_keep)))

    # Perform database operations
    with transaction.atomic():
        # Expire ranges
        if ranges_to_expire:
            IpRange.objects.filter(
                ipRangeId__in=[r.ipRangeId for r in ranges_to_expire]
            ).update(expiredAt=timezone.now())
            print("\nExpired {} IP ranges".format(len(ranges_to_expire)))

        # Reactivate ranges
        if ranges_to_reactivate:
            IpRange.objects.filter(
                ipRangeId__in=[r['db_range'].ipRangeId for r in ranges_to_reactivate]
            ).update(expiredAt=None)
            print("Reactivated {} IP ranges".format(len(ranges_to_reactivate)))

        # Add new ranges
        for range_info in ranges_to_add:
            try:
                IpRange.objects.create(
                    partyId=party_id,
                    start=range_info['start'],
                    end=range_info['end'],
                    startLong=range_info['start_long'],
                    endLong=range_info['end_long']
                )
            except Exception as e:
                print("Error adding IP range {} - {}: {}".format(
                    range_info['start'],
                    range_info['end'],
                    e
                ))
        print("Added {} new IP ranges".format(len(ranges_to_add)))

if __name__ == "__main__":
    update_ip_ranges()