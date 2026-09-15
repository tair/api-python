#!/usr/bin/python
"""
Tests for the cutoffs a run computes.

The digest itself is not tested here. Its only public surface returns a
rendered string, so every assertion against it is a substring match on
presentation -- weaker evidence than looking at a rendered sample, and a
standing cost every time the presentation changes. Render a sample and read it
instead.

What is left is date arithmetic: data in, data out, and two traps that are
invisible in a rendered digest.

  python scripts/testNotifyExpiringSubscriptions.py
"""
import os
import sys
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dateutil.relativedelta import relativedelta

from subscription.expirationnotice import expirationWindows

NOW = datetime(2026, 8, 19, 4, 0, 0)

EXPIRATION_HORIZONS = (
    relativedelta(days=90),
    relativedelta(days=7),
    relativedelta(days=60),
    relativedelta(days=30),
)

passed = 0
failed = 0


def assert_test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS: %s" % name)
    else:
        failed += 1
        print("  FAIL: %s%s" % (name, (" -- %s" % detail) if detail else ""))


def test_cutoffs_land_on_the_last_second_of_each_day():
    print("\nCutoffs")

    bounds = expirationWindows.cutoffs(EXPIRATION_HORIZONS, NOW)

    assert_test(
        "one cutoff per horizon",
        len(bounds) == len(EXPIRATION_HORIZONS),
    )
    assert_test(
        "cutoffs come back soonest first whatever order the horizons arrive in",
        [h.days for h, _ in bounds] == [7, 30, 60, 90],
    )
    assert_test(
        "the furthest cutoff is last, so the caller can take it for the query",
        bounds[-1][1] == datetime(2026, 11, 17, 23, 59, 59),
    )
    assert_test(
        "every cutoff is the last second of its day",
        all(c.hour == 23 and c.minute == 59 and c.second == 59 and c.microsecond == 0
            for _, c in bounds),
        "endDate is stored at 23:59:59, and MySQL DATETIME rounds .999999 up a day",
    )


def test_cutoffs_do_not_depend_on_the_time_of_day():
    print("\nRun time independence")

    early = expirationWindows.cutoffs(EXPIRATION_HORIZONS, datetime(2026, 8, 19, 0, 5, 0))
    late = expirationWindows.cutoffs(EXPIRATION_HORIZONS, datetime(2026, 8, 19, 23, 50, 0))
    assert_test(
        "a run at 00:05 and one at 23:50 ask for the same cutoffs",
        early == late,
        "cron time would otherwise shift which subscriptions are reported",
    )


def main():
    print("Expiration notifier: cutoffs")

    test_cutoffs_land_on_the_last_second_of_each_day()
    test_cutoffs_do_not_depend_on_the_time_of_day()

    print("\n%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
