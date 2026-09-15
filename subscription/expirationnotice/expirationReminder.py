import logging

from django.core.mail import send_mail

from . import digest

logger = logging.getLogger(__name__)

SENDER = 'subscriptions@phoenixbioinformatics.org'
RECIPIENTS = ('techteam@arabidopsis.org', 'info@phoenixbioinformatics.org')

# The digest is a table, so it is sent as HTML only. This stands in for the
# plain-text alternative rather than restating the digest, which would be a
# second rendering of the same rows, free to drift from the first.
TEXT_ALTERNATIVE = ('This is an HTML message listing institutional '
                    'subscriptions approaching expiration, and needs a mail '
                    'client that can display HTML.')


def send(subscriptions):
    send_mail(
        subject='Institutional subscriptions approaching expiration (%d)'
                % len(subscriptions),
        message=TEXT_ALTERNATIVE,
        html_message=digest.render(subscriptions),
        from_email=SENDER,
        recipient_list=list(RECIPIENTS),
    )
    logger.info('reminder for %d sent to %s', len(subscriptions),
                ', '.join(RECIPIENTS))
