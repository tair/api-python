import logging

from django.core.mail import send_mail

from . import digest

logger = logging.getLogger(__name__)

SENDER = 'subscriptions@phoenixbioinformatics.org'
RECIPIENTS = ('techteam@arabidopsis.org', 'info@phoenixbioinformatics.org')


def send(subscriptions, bounds):
    send_mail(
        subject='Institutional subscriptions approaching expiration (%d)'
                % len(subscriptions),
        message=digest.render(subscriptions, bounds),
        from_email=SENDER,
        recipient_list=list(RECIPIENTS),
    )
    logger.info('reminder for %d sent to %s', len(subscriptions),
                ', '.join(RECIPIENTS))
