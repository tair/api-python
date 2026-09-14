from common.utils.dateUtils import last_second_of_day, relativedelta_sort_key


def cutoffs(horizons, now):
    run_day = last_second_of_day(now)
    return [
        (horizon, run_day + horizon)
        for horizon in sorted(horizons, key=relativedelta_sort_key)
    ]
