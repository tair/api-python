import logging
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from common.utils.dateUtils import start_of_day

from . import expirationReminder, expiring, runLog

logger = logging.getLogger(__name__)

EXPIRATION_HORIZON = relativedelta(months=1)


def notify(now):
    start = start_of_day(now)
    # Inclusive end: the second before the next run's window opens.
    end = start + EXPIRATION_HORIZON - timedelta(seconds=1)

    subscriptions = expiring.between(start, end)
    logger.info('[%s .. %s] %d expiring', start, end, len(subscriptions))

    if subscriptions:
        expirationReminder.send(subscriptions)

    runLog.record(run_date=now, success=True)
    return subscriptions
