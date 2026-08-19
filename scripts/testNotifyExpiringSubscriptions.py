#!/usr/bin/python
"""
Tests for the parts of the expiration notifier that need no database.

Covers the end-date windows each reminder asks for, the wording derived from
them, and the digest and failure bodies. Reading subscriptions, writing the run
log and sending mail are left to a run against the test database.

  python scripts/testNotifyExpiringSubscriptions.py
"""
import os
import sys
from collections import namedtuple
from datetime import datetime, time, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dateutil.relativedelta import relativedelta

from subscription.expirationnotice import digest, expirationWindows, failure
from subscription.expirationnotice.digest import Due

NOW = datetime(2026, 8, 17, 4, 0, 0)
YESTERDAY = NOW - timedelta(days=1)

WEEK = relativedelta(weeks=1)
MONTH = relativedelta(months=1)
THREE_MONTHS = relativedelta(months=3)
LEAD_TIMES = (THREE_MONTHS, MONTH, WEEK)
HORIZON = timedelta(days=4)

Row = namedtuple('Row', ['partner_id', 'party_type', 'name', 'end_date'])

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


def row(day=21, name='Test University', party_type='organization'):
    return Row(
        partner_id='tair',
        party_type=party_type,
        name=name,
        end_date=datetime(2026, 8, day, 23, 59, 59),
    )


def heading_for(lead_time):
    return digest.render([Due(lead_time=lead_time, expiring=[row()])]).splitlines()[0]


def windows_for(last_success, now=NOW):
    return expirationWindows.compute(LEAD_TIMES, HORIZON, last_success, now)


def window(lead_time, last_success, now=NOW):
    for found, start, end in windows_for(last_success, now):
        if found == lead_time:
            return start, end
    raise AssertionError('no window for %r' % lead_time)


def test_windows_end_at_end_of_day():
    print("\nDay snapping")

    _, end = window(MONTH, YESTERDAY)
    assert_test(
        "the window ends at the last second of the day",
        end == datetime(2026, 9, 17, 23, 59, 59),
        "endDate is stored at 23:59:59, so a bound at 04:00 would miss it",
    )
    assert_test(
        "microseconds are zero",
        end.microsecond == 0,
        "MySQL DATETIME has no fractional seconds and rounds .999999 up a day",
    )


def test_windows_do_not_depend_on_the_time_of_day():
    print("\nRun time independence")

    early = windows_for(YESTERDAY, datetime(2026, 8, 17, 0, 5, 0))
    late = windows_for(YESTERDAY, datetime(2026, 8, 17, 23, 50, 0))
    assert_test(
        "a run at 00:05 and one at 23:50 ask for the same windows",
        early == late,
        "cron time would otherwise shift which subscriptions are reported",
    )


def covered_days(lead_time, last_success, now=NOW):
    start, end = window(lead_time, last_success, now)
    if start > end:
        return 0
    return (end.date() - start.date()).days + 1


def test_windows_cover_whole_days_back_to_the_horizon():
    print("\nBackfill horizon")

    start, end = window(WEEK, YESTERDAY)
    assert_test(
        "a window starts at midnight",
        start.time() == time(0, 0, 0),
        "one second past the previous window's last second is the day boundary",
    )
    assert_test(
        "a window ends at the last second of its final day",
        end.time() == time(23, 59, 59),
    )
    assert_test(
        "one day since the last success covers exactly that day",
        start.date() == end.date() and covered_days(WEEK, YESTERDAY) == 1,
    )
    assert_test(
        "a first run covers the backfill horizon in whole days",
        covered_days(WEEK, None) == HORIZON.days,
    )
    assert_test(
        "a long outage is capped at the backfill horizon",
        covered_days(WEEK, NOW - timedelta(days=400)) == HORIZON.days,
    )
    assert_test(
        "a second run the same day covers nothing",
        covered_days(WEEK, NOW) == 0,
        "an empty window means the digest is not sent twice in a day",
    )


def test_no_window_can_reach_an_expired_subscription():
    print("\nExpired subscriptions")

    for last_success in (None, NOW - timedelta(days=400), YESTERDAY, NOW):
        starts = [start for _, start, _ in windows_for(last_success)]
        assert_test(
            "no window starts before now (%s)" % (last_success or 'first run'),
            all(start >= NOW for start in starts),
            "the horizon must stay under the soonest lead time",
        )


def test_windows_do_not_overlap():
    print("\nDisjointness")

    for last_success in (None, NOW - timedelta(days=400), YESTERDAY):
        bounds = sorted((start, end) for _, start, end in windows_for(last_success))
        assert_test(
            "windows are disjoint (%s)" % (last_success or 'first run'),
            all(a[1] < b[0] for a, b in zip(bounds, bounds[1:])),
            "bounds are inclusive, so a shared instant would report twice",
        )


def test_consecutive_runs_tile_exactly():
    print("\nRun-to-run tiling")

    today = windows_for(YESTERDAY, NOW)
    tomorrow = windows_for(NOW, NOW + timedelta(days=1))
    pairs = list(zip(today, tomorrow))

    assert_test(
        "tomorrow's window starts after today's ends",
        all(mine[2] < next_run[1] for mine, next_run in pairs),
        "an overlap would report the same subscription on two consecutive days",
    )
    assert_test(
        "and leaves no gap between them",
        all((next_run[1] - mine[2]) == timedelta(seconds=1) for mine, next_run in pairs),
        "a gap would let a subscription slip past both runs unreported",
    )


def test_sections_come_out_soonest_first():
    print("\nOrdering")

    body = digest.render([
        Due(lead_time=THREE_MONTHS, expiring=[row(day=30, name='Loose University')]),
        Due(lead_time=WEEK, expiring=[row(day=21, name='Urgent College')]),
        Due(lead_time=MONTH, expiring=[row(day=25, name='Middling Institute')]),
    ])
    order = [body.index(name) for name in ('Urgent College', 'Middling Institute', 'Loose University')]
    assert_test(
        "the soonest reminder is rendered first whatever order it arrives in",
        order == sorted(order),
        "relativedelta has no ordering of its own, so it is applied to a date",
    )


def test_headings_are_derived_from_the_lead_time():
    print("\nHeadings")

    assert_test("a week reads as 'a week'", heading_for(WEEK).endswith('a week'))
    assert_test("one month is singular", heading_for(MONTH).endswith('a month'))
    assert_test(
        "counts above one use a numeral and a plural unit",
        heading_for(THREE_MONTHS).endswith('3 months'),
    )
    assert_test(
        "a fortnight collapses to weeks",
        heading_for(relativedelta(weeks=2)).endswith('2 weeks'),
    )
    assert_test(
        "days that are not whole weeks stay days",
        heading_for(relativedelta(days=10)).endswith('10 days'),
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
    assert_test(
        "an unwordable lead_time raises rather than printing a repr",
        raised,
    )


def line_for(body, name):
    return [line for line in body.splitlines() if name in line][0]


def test_digest_reports_every_subscription_under_its_own_heading():
    print("\nDigest")

    body = digest.render([
        Due(lead_time=WEEK, expiring=[row(day=21, name='Urgent College')]),
        Due(lead_time=THREE_MONTHS, expiring=[
            row(day=30, name='Loose University'),
            row(day=31, name='Padova'),
        ]),
    ])

    assert_test(
        "every subscription given is reported",
        all(name in body for name in ('Urgent College', 'Loose University', 'Padova')),
        "a dropped subscription is a renewal nobody chases",
    )
    assert_test(
        "each subscription falls under the heading for its own lead time",
        body.index('Urgent College')
        < body.index(heading_for(THREE_MONTHS))
        < body.index('Loose University'),
    )
    assert_test(
        "a subscription's line carries its date, name, partner and party type",
        all(fact in line_for(body, 'Urgent College')
            for fact in ('2026-08-21', 'Urgent College', 'tair', 'organization')),
    )
    assert_test(
        "a consortium is reported as a consortium",
        'consortium' in line_for(
            digest.render([Due(lead_time=WEEK, expiring=[row(party_type='consortium')])]),
            'Test University',
        ),
    )


def test_failure_body_carries_the_trace():
    print("\nFailure alert")

    body = failure.render(NOW, "ValueError: database is on fire")
    assert_test("the traceback is included", 'ValueError: database is on fire' in body)
    assert_test("the run date is given", '2026-08-17' in body)


def main():
    print("Expiration notifier: tests that need no database")

    test_windows_end_at_end_of_day()
    test_windows_do_not_depend_on_the_time_of_day()
    test_windows_cover_whole_days_back_to_the_horizon()
    test_no_window_can_reach_an_expired_subscription()
    test_windows_do_not_overlap()
    test_consecutive_runs_tile_exactly()
    test_sections_come_out_soonest_first()
    test_headings_are_derived_from_the_lead_time()
    test_digest_reports_every_subscription_under_its_own_heading()
    test_failure_body_carries_the_trace()

    print("\n%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
