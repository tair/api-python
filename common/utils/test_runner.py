import logging

from django.test.runner import DiscoverRunner
from django.conf import settings

class NoLoggingTestRunner(DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):

        # Don't show logging messages while testing
        logging.disable(logging.CRITICAL)

        return super(NoLoggingTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)
