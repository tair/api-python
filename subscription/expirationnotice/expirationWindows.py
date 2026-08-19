from datetime import timedelta

from common.utils.dateUtils import last_second_of_day


def compute(lead_times, backfill_horizon, last_success, now):
    run_day = last_second_of_day(now)
    lookback_period = _lookback_period(last_success, run_day, backfill_horizon)
    return [
        (lead_time,) + _get_window(run_day, lead_time, lookback_period)
        for lead_time in lead_times
    ]


def _lookback_period(last_success, run_day, backfill_horizon):
    elapsed_time = run_day - last_second_of_day(last_success or run_day - backfill_horizon)
    return min(elapsed_time, backfill_horizon)


def _get_window(run_day, lead_time, lookback_period):
    end = run_day + lead_time
    start = _start_of_next_day(end - lookback_period)
    return (start, end)


def _start_of_next_day(end_of_day):
    return end_of_day + timedelta(seconds=1)
