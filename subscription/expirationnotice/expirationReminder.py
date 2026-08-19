import logging

from django.core.mail import send_mail

from . import digest

logger = logging.getLogger(__name__)

SENDER = 'subscriptions@phoenixbioinformatics.org'
RECIPIENTS = ('techteam@arabidopsis.org', 'info@phoenixbioinformatics.org')


def send(due):
    count = sum(len(group.expiring) for group in due)
    send_mail(
        subject='Institutional subscriptions approaching expiration (%d)' % count,
        message=digest.render(due),
        from_email=SENDER,
        recipient_list=list(RECIPIENTS),
    )
    logger.info('reminder for %d sent to %s', count, ', '.join(RECIPIENTS))
