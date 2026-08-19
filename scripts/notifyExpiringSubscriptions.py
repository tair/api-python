#!/usr/bin/python
"""
Email staff one digest of institutional subscriptions approaching expiration.

Safe to run late, twice, or after a missed day: each run covers the period
since the last successful one.

Run once per day via cron, e.g.:
  0 4 * * * cd /var/www/api-python && python scripts/notifyExpiringSubscriptions.py

Nothing in this repository installs that entry. Timestamped lines go to stdout
and no log file is opened, so redirect or collect them as the deployment
prefers. Exits non-zero if the run failed, having tried to email the tech team.
"""
import logging
import os
import sys
import traceback
from datetime import timedelta

import django
from dateutil.relativedelta import relativedelta

PARTNERS = ('tair',)

LEAD_TIMES = (
    relativedelta(months=3),
    relativedelta(months=1),
    relativedelta(weeks=1),
)

BACKFILL_HORIZON = timedelta(days=4)

logger = logging.getLogger('subscription.expirationnotice')


def bootstrap_django():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
    django.setup()


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %H:%M:%S')
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def record_failure(run_date, err):
    from subscription.expirationnotice import runLog

    try:
        runLog.record(run_date=run_date, success=False, message=str(err)[:1000])
    except Exception as record_error:
        logger.error('could not record the failed run: %s', record_error)


def handle_error(run_date, err, trace):
    from subscription.expirationnotice import failureReport

    logger.error('run failed\n%s', trace)
    failureReport.send(run_date, trace)
    record_failure(run_date, err)


def main():
    bootstrap_django()
    configure_logging()

    from django.utils import timezone
    now = timezone.now()

    try:
        from subscription.expirationnotice.notifier import notify
        notify(
            partners=PARTNERS,
            lead_times=LEAD_TIMES,
            backfill_horizon=BACKFILL_HORIZON,
            now=now,
        )
    except Exception as err:
        handle_error(now, err, traceback.format_exc())
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
