#!/usr/bin/python
"""
Tests for the cutoff a run computes.

The digest itself is not tested here. Its only public surface returns a
rendered string, so every assertion against it is a substring match on
presentation -- weaker evidence than looking at a rendered sample, and a
standing cost every time the presentation changes. Render a sample and read it
instead.

What is left is date arithmetic: data in, data out, over traps that are
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

from common.utils.dateUtils import start_of_day
from subscription.expirationnotice import expirationWindows

MONTH = relativedelta(months=1)

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


def test_the_cutoff_is_the_last_second_of_its_day():
    print("\nCutoff")

    cutoff = expirationWindows.cutoff(MONTH, datetime(2026, 8, 19, 4, 0, 0))

    assert_test(
        "the cutoff is the last second of its day",
        cutoff == datetime(2026, 9, 19, 23, 59, 59),
        "endDate is stored at 23:59:59, and MySQL DATETIME rounds .999999 up a day",
    )


def test_the_cutoff_does_not_depend_on_the_time_of_day():
    print("\nRun time independence")

    early = expirationWindows.cutoff(MONTH, datetime(2026, 8, 19, 0, 5, 0))
    late = expirationWindows.cutoff(MONTH, datetime(2026, 8, 19, 23, 50, 0))
    assert_test(
        "a run at 00:05 and one at 23:50 ask for the same cutoff",
        early == late,
        "cron time would otherwise shift which subscriptions are reported",
    )


def test_a_run_reaches_the_next_one_whatever_the_month_length():
    print("\nMonth lengths")

    # The first of every month of a year that includes a February of 28 days,
    # paired with the first of the month after it.
    for month in range(1, 13):
        run = datetime(2026, month, 1, 4, 0, 0)
        following = datetime(2026 + month // 12, month % 12 + 1, 1, 4, 0, 0)

        assert_test(
            "a run on %s covers up to the run on %s"
            % (run.date(), following.date()),
            expirationWindows.cutoff(MONTH, run) >= start_of_day(following),
            "a subscription ending in the gap would first be reported on the "
            "day it expires",
        )

    assert_test(
        "30 days would not, across a 31-day month",
        expirationWindows.cutoff(relativedelta(days=30), datetime(2026, 1, 1, 4, 0, 0))
        < start_of_day(datetime(2026, 2, 1, 4, 0, 0)),
        "this is why the horizon is a month rather than 30 days",
    )


def main():
    print("Expiration notifier: cutoff")

    test_the_cutoff_is_the_last_second_of_its_day()
    test_the_cutoff_does_not_depend_on_the_time_of_day()
    test_a_run_reaches_the_next_one_whatever_the_month_length()

    print("\n%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
