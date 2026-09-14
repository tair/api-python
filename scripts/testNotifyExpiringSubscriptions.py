#!/usr/bin/python
"""
Tests for the parts of the expiration notifier that need no database.

Covers the cutoffs a run computes, how rows are grouped by horizon,
the wording derived from each lead time, and the digest and failure bodies.
Reading subscriptions, writing the run log and sending mail are left to a run
against the test database.

  python scripts/testNotifyExpiringSubscriptions.py
"""
import os
import sys
from collections import namedtuple
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dateutil.relativedelta import relativedelta

from subscription.expirationnotice import digest, expirationWindows, failure

NOW = datetime(2026, 8, 19, 4, 0, 0)

WEEK = relativedelta(days=7)
THIRTY = relativedelta(days=30)
SIXTY = relativedelta(days=60)
NINETY = relativedelta(days=90)
EXPIRATION_HORIZONS = (NINETY, WEEK, SIXTY, THIRTY)

Row = namedtuple('Row', ['party_type', 'name', 'start_date', 'end_date'])

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


def row(days_out=2, name='Test University', party_type='organization', started=True):
    end_date = (NOW + timedelta(days=days_out)).replace(
        hour=23, minute=59, second=59, microsecond=0)
    return Row(
        party_type=party_type,
        name=name,
        start_date=end_date - relativedelta(years=1) if started else None,
        end_date=end_date,
    )


BOUNDS = None  # set in main once expirationWindows is available


def heading_for(horizon):
    return digest.render([row()], [(horizon, NOW + relativedelta(years=50))]).splitlines()[0]


def heading_of(days_out):
    return digest.render([row(days_out=days_out)], BOUNDS).splitlines()[0]


def line_for(body, name):
    return [line for line in body.splitlines() if name in line][0]


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


def rendered(days_out):
    rows = [row(days_out=d, name='day %d' % d) for d in days_out]
    return digest.render(rows, BOUNDS)


def test_rows_land_under_the_soonest_horizon_that_fits():
    print("\nHorizons")

    for days_out, expected in ((0, WEEK), (1, WEEK), (7, WEEK), (8, THIRTY),
                               (30, THIRTY), (31, SIXTY), (60, SIXTY),
                               (61, NINETY), (90, NINETY)):
        assert_test(
            "%d days out is reported under the %d-day heading"
            % (days_out, expected.days),
            heading_of(days_out) == heading_for(expected),
        )


def test_grouping_places_every_row_exactly_once():
    print("\nGrouping completeness")

    days_out = [0, 1, 7, 8, 30, 31, 60, 61, 90]
    body = rendered(days_out)

    assert_test(
        "every row is reported",
        all('day %d' % d in body for d in days_out),
        "a dropped row is a renewal nobody chases",
    )
    assert_test(
        "no row is reported twice",
        all(body.count('day %d ' % d) == 1 for d in days_out),
    )
    assert_test(
        "only occupied horizons get a heading",
        rendered([1]).count('Expiring within') == 1,
    )
    assert_test(
        "within a heading the query's order is kept",
        [line.split('day ')[1].split()[0]
         for line in rendered([7, 1, 0]).splitlines() if 'day ' in line] == ['7', '1', '0'],
        "expiring.between already orders by endDate, so grouping must not reshuffle",
    )


def test_sections_follow_the_order_of_the_bounds():
    print("\nOrdering")

    body = digest.render(
        [row(days_out=80, name='Loose University'),
         row(days_out=2, name='Urgent College'),
         row(days_out=20, name='Middling Institute')],
        BOUNDS,
    )
    order = [body.index(name) for name
             in ('Urgent College', 'Middling Institute', 'Loose University')]
    assert_test(
        "sections are rendered in the order the bounds give",
        order == sorted(order),
        "cutoffs guarantees soonest first, so the digest does not re-sort",
    )


def test_headings_are_derived_from_the_lead_time():
    print("\nHeadings")

    assert_test("a week reads as 'a week'", heading_for(WEEK).endswith('a week'))
    assert_test("thirty days reads as days", heading_for(THIRTY).endswith('30 days'))
    assert_test("ninety days reads as days", heading_for(NINETY).endswith('90 days'))
    assert_test("one month is singular",
                heading_for(relativedelta(months=1)).endswith('a month'))
    assert_test(
        "counts above one use a numeral and a plural unit",
        heading_for(relativedelta(months=3)).endswith('3 months'),
    )
    assert_test(
        "45 days is not called 6 weeks",
        heading_for(relativedelta(days=45)).endswith('45 days'),
        "relativedelta.weeks is days // 7, so it reports 6 for 45 days",
    )
    assert_test(
        "a whole year stays a year",
        heading_for(relativedelta(months=12)).endswith('a year'),
    )
    assert_test(
        "months beyond a year are expressed in months",
        heading_for(relativedelta(months=14)).endswith('14 months'),
        "relativedelta normalises 14 months to years=1 months=2",
    )

    try:
        heading_for(relativedelta(hours=3))
        raised = False
    except ValueError:
        raised = True
    assert_test("an unwordable lead time raises rather than printing a repr", raised)


def test_digest_reports_every_subscription_under_its_own_heading():
    print("\nDigest")

    body = digest.render(
        [row(days_out=2, name='Urgent College'),
         row(days_out=80, name='Loose University'),
         row(days_out=85, name='Padova')],
        BOUNDS,
    )

    assert_test(
        "every subscription given is reported",
        all(name in body for name in ('Urgent College', 'Loose University', 'Padova')),
        "a dropped subscription is a renewal nobody chases",
    )
    assert_test(
        "each subscription falls under the heading for its own lead time",
        body.index('Urgent College')
        < body.index(heading_for(NINETY))
        < body.index('Loose University'),
    )
    assert_test(
        "a line carries both term dates, the name and the party type",
        all(fact in line_for(body, 'Urgent College')
            for fact in ('2026-08-21', '2025-08-21', 'Urgent College', 'organization')),
    )
    assert_test(
        "a consortium is reported as a consortium",
        'consortium' in line_for(
            digest.render([row(party_type='consortium')], BOUNDS), 'Test University',
        ),
    )
    assert_test(
        "a missing start date does not break the line",
        'organization' in line_for(
            digest.render([row(started=False)], BOUNDS), 'Test University',
        ),
        "Subscription.startDate is nullable",
    )


def test_failure_body_carries_the_trace():
    print("\nFailure alert")

    body = failure.render(NOW, "ValueError: database is on fire")
    assert_test("the traceback is included", 'ValueError: database is on fire' in body)
    assert_test("the run date is given", '2026-08-19' in body)


def main():
    global BOUNDS
    BOUNDS = expirationWindows.cutoffs(EXPIRATION_HORIZONS, NOW)

    print("Expiration notifier: tests that need no database")

    test_cutoffs_land_on_the_last_second_of_each_day()
    test_cutoffs_do_not_depend_on_the_time_of_day()
    test_rows_land_under_the_soonest_horizon_that_fits()
    test_grouping_places_every_row_exactly_once()
    test_sections_follow_the_order_of_the_bounds()
    test_headings_are_derived_from_the_lead_time()
    test_digest_reports_every_subscription_under_its_own_heading()
    test_failure_body_carries_the_trace()

    print("\n%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
