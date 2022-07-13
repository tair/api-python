import django
import unittest
import sys
import json
from django.test import TestCase
from .testSamples import UsageSample
from django.core.mail import send_mail
from django.test.utils import override_settings

# test for API end point /parties/usage/
# API used for requesting usage for consortiums/institutions
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class GetUsageRequestTest(TestCase):
    sample = UsageSample()

    def test_for_send_usage_request(self):
        self.send_usage_email(self.sample.institutionData)
        self.send_usage_email(self.sample.consortiumData)

    # this code is copied from party/views.py implementation
    # since the original implementation hard coded recipient email
    def send_usage_email(self, data):
        partyName = ''
        partyTypeName = ''
        if data['institution']:
            partyName = data['institution']
            partyTypeName = 'Institution'
        elif data['consortium']:
            partyName = data['consortium']
            partyTypeName = 'Consortium'
        subject = "%s Usage Request For %s" % (partyTypeName,partyName)
        message = "Partner: %s\n" \
                  "%s: %s\n" \
                  "User: %s\n" \
                  "Email: %s\n" \
                  "Start date: %s\n" \
                  "End date: %s\n" \
                  "Comments: %s\n" \
                  % (data['partner'], partyTypeName, partyName, data['name'], data['email'], data['startDate'], data['endDate'], data['comments'])
        from_email = "subscriptions@phoenixbioinformatics.org"
        recipient_list = [self.sample.RECEIPIENT_EMAIL]
        self.assertEqual(send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False), 1)

print("Running unit tests on consortium usage email request.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)