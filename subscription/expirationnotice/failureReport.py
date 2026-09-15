import logging

from django.core.mail import send_mail

from . import failure

logger = logging.getLogger(__name__)

SENDER = 'subscriptions@phoenixbioinformatics.org'
RECIPIENTS = ('techteam@arabidopsis.org',)


def send(run_date, trace):
    try:
        send_mail(
            subject='Institutional subscription expiration notifier failed',
            message=failure.render(run_date, trace),
            from_email=SENDER,
            recipient_list=list(RECIPIENTS),
        )
        logger.info('failure report sent to %s', ', '.join(RECIPIENTS))
    except Exception as alert_error:
        logger.error('could not send the failure report: %s', alert_error)
