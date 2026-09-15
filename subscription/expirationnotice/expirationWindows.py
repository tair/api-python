from common.utils.dateUtils import last_second_of_day


def cutoff(horizon, now):
    return last_second_of_day(now) + horizon
