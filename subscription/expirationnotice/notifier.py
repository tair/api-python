import logging

from common.utils.dateUtils import start_of_day

from . import expirationReminder, expirationWindows, expiring, runLog

logger = logging.getLogger(__name__)


def notify(partners, horizons, now):
    bounds = expirationWindows.cutoffs(horizons, now)
    _, furthest = bounds[-1]
    start = start_of_day(now)

    subscriptions = expiring.between(partners, start, furthest)
    logger.info('[%s .. %s] %d expiring', start, furthest, len(subscriptions))

    if subscriptions:
        expirationReminder.send(subscriptions, bounds)

    runLog.record(run_date=now, success=True)
    return subscriptions
