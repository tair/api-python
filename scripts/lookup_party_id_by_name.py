#!/usr/bin/python
"""
Resolve organization name to Party.partyId (read-only). Use when building the bulk-party
Excel: column **party id** must match a row in Party.

Usage (from project root, same env as other Django scripts):
  python scripts/lookup_party_id_by_name.py "University"
  python scripts/lookup_party_id_by_name.py --exact "Some Library Name"

Prints: partyId<TAB>name (up to 100 rows). If multiple matches, disambiguate with the user
before loading IPs.
"""
from __future__ import print_function

import argparse
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')

import django  # noqa: E402

django.setup()

from party.models import Party  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("name", help="Institution name or substring to search")
    p.add_argument(
        "--exact",
        action="store_true",
        help="Match Party.name with case-insensitive exact match",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Max rows to print (default 100)",
    )
    args = p.parse_args()

    qs = Party.objects.all()
    if args.exact:
        qs = qs.filter(name__iexact=args.name.strip())
    else:
        qs = qs.filter(name__icontains=args.name.strip())

    qs = qs.order_by("partyId")[: max(1, args.limit)]
    rows = list(qs)
    if not rows:
        print("No Party rows matched.", file=sys.stderr)
        return 1
    for row in rows:
        print("%s\t%s" % (row.partyId, row.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
