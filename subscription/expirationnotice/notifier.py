import logging

from . import expirationReminder, expirationWindows, expiring, runLog
from .digest import Due

logger = logging.getLogger(__name__)


def notify(partners, lead_times, backfill_horizon, now):
    last_success = runLog.last_success()
    logger.info('last success %s', last_success or '(first run)')

    due = []
    for lead_time, start, end in expirationWindows.compute(lead_times, backfill_horizon, last_success, now):
        found = expiring.between(partners, start, end)
        logger.info('[%s .. %s] %d expiring', start, end, len(found))
        if found:
            due.append(Due(lead_time=lead_time, expiring=found))

    if due:
        expirationReminder.send(due)

    runLog.record(run_date=now, success=True)
    return due
