import logging

from common.utils.dateUtils import start_of_day

from . import expirationReminder, expirationWindows, expiring, runLog

logger = logging.getLogger(__name__)


def notify(horizon, now):
    start = start_of_day(now)
    end = expirationWindows.cutoff(horizon, now)

    subscriptions = expiring.between(start, end)
    logger.info('[%s .. %s] %d expiring', start, end, len(subscriptions))

    if subscriptions:
        expirationReminder.send(subscriptions)

    runLog.record(run_date=now, success=True)
    return subscriptions
