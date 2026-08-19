from datetime import datetime


def relativedelta_sort_key(relative_delta):
    base_date = datetime(2000, 1, 1)
    return base_date + relative_delta


def last_second_of_day(moment):
    return moment.replace(hour=23, minute=59, second=59, microsecond=0)
