def start_of_day(moment):
    return moment.replace(hour=0, minute=0, second=0, microsecond=0)


def last_second_of_day(moment):
    return moment.replace(hour=23, minute=59, second=59, microsecond=0)
