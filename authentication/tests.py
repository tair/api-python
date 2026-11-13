import hashlib
import json

from django.core import mail
from django.test import TestCase

from authentication import recovery
from authentication.models import Credential, AccountRecoveryAttempt, AccountRecoveryLock
from partner.models import Partner
from party.models import Party

RESET_URL = '/credentials/resetPwd/'
USERNAMES_URL = '/credentials/getUsernames/'


class AccountRecoveryTestBase(TestCase):
    def setUp(self):
        self.partner = Partner.objects.create(
            partnerId='tair', name='TAIR', logoUri='', termOfServiceUri='')
        party = Party.objects.create(name='Curator')
        self.originalHash = hashlib.sha1('original').hexdigest()
        self.credential = Credential.objects.create(
            username='curator', password=self.originalHash,
            email='curator@arabidopsis.org', partyId=party, partnerId=self.partner)

    def reset(self, username='curator', ip='10.0.0.1'):
        return self.client.put(
            RESET_URL + '?user=%s&partnerId=tair' % username, REMOTE_ADDR=ip)

    def getUsernames(self, email='curator@arabidopsis.org', ip='10.0.0.1'):
        return self.client.get(
            USERNAMES_URL, {'email': email, 'partnerId': 'tair'}, REMOTE_ADDR=ip)


class ResetPwdTest(AccountRecoveryTestBase):
    def test_response_has_no_password_hash_or_full_email(self):
        response = self.reset()
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertNotIn('temppwd', body)
        self.assertEqual(body['useremail'], 'c*****r@arabidopsis.org')
        self.assertNotIn('curator@arabidopsis.org', response.content)
        credential = Credential.objects.get(pk=self.credential.pk)
        self.assertNotIn(credential.password, response.content)
        self.assertNotEqual(credential.password, self.originalHash)
        self.assertEqual(len(mail.outbox), 1)

    def test_unknown_user_still_401(self):
        response = self.reset(username='nobody')
        self.assertEqual(response.status_code, 401)

    def test_rate_limited_per_username(self):
        maxCount = recovery.RESET_PER_USERNAME[1]
        for i in range(maxCount):
            # Different IPs, and different letter case, still count as one user.
            username = 'CURATOR' if i % 2 else 'curator'
            self.assertEqual(self.reset(username=username, ip='10.0.0.%d' % i).status_code, 200)
        passwordBefore = Credential.objects.get(pk=self.credential.pk).password
        response = self.reset(ip='10.0.1.1')
        self.assertEqual(response.status_code, 429)
        # A blocked request neither emails nor changes the password.
        self.assertEqual(len(mail.outbox), maxCount)
        self.assertEqual(Credential.objects.get(pk=self.credential.pk).password, passwordBefore)

    def test_rate_limited_per_ip(self):
        maxCount = recovery.RESET_PER_IP[1]
        for i in range(maxCount):
            self.assertEqual(self.reset(username='nobody%d' % i).status_code, 401)
        self.assertEqual(self.reset().status_code, 429)
        self.assertEqual(self.reset(ip='10.0.0.2').status_code, 200)

    def test_attempts_store_hashes_not_values(self):
        self.reset()
        for attempt in AccountRecoveryAttempt.objects.all():
            self.assertEqual(len(attempt.keyHash), 40)
            self.assertNotIn('curator', attempt.keyHash)


class GetUsernamesTest(AccountRecoveryTestBase):
    def test_usernames_only_emailed(self):
        response = self.getUsernames()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(json.loads(response.content).keys()), ['message'])
        self.assertNotIn('curator', response.content)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('curator', mail.outbox[0].body)

    def test_unknown_email_gets_same_response(self):
        known = self.getUsernames()
        unknown = self.getUsernames(email='nobody@example.org')
        self.assertEqual(unknown.status_code, known.status_code)
        self.assertEqual(unknown.content, known.content)
        # Only the registered address is emailed.
        self.assertEqual(len(mail.outbox), 1)

    def test_mail_failure_gets_same_response(self):
        from authentication import views
        unknown = self.getUsernames(email='nobody@example.org')
        realSendMail = views.send_mail
        def failingSendMail(**kwargs):
            raise IOError('SMTP is down')
        views.send_mail = failingSendMail
        try:
            known = self.getUsernames()
        finally:
            views.send_mail = realSendMail
        self.assertEqual(known.status_code, unknown.status_code)
        self.assertEqual(known.content, unknown.content)

    def test_unknown_partner(self):
        response = self.client.get(USERNAMES_URL, {'email': 'curator@arabidopsis.org', 'partnerId': 'nope'})
        self.assertEqual(response.status_code, 400)

    def test_rate_limited_per_email(self):
        maxCount = recovery.USERNAMES_PER_EMAIL[1]
        for i in range(maxCount):
            self.assertEqual(self.getUsernames(ip='10.0.0.%d' % i).status_code, 200)
        self.assertEqual(self.getUsernames(ip='10.0.1.1').status_code, 429)
        self.assertEqual(len(mail.outbox), maxCount)


class MaskEmailTest(TestCase):
    def test_mask(self):
        self.assertEqual(recovery.maskEmail('a@x.org'), '*@x.org')
        self.assertEqual(recovery.maskEmail('ab@x.org'), 'a*@x.org')
        self.assertEqual(recovery.maskEmail('abcd@x.org'), 'a**d@x.org')
        self.assertEqual(recovery.maskEmail(None), '')

    def test_mask_is_idempotent(self):
        for email in ['a@x.org', 'ab@x.org', 'abcd@x.org']:
            once = recovery.maskEmail(email)
            self.assertEqual(recovery.maskEmail(once), once)


class ReserveTest(TestCase):
    def test_all_or_nothing(self):
        userLimit = ('reset-user', 3)
        ipLimit = ('reset-ip', 1)
        self.assertTrue(recovery.reserve([(userLimit, 'u1'), (ipLimit, '1.1.1.1')]))
        # The IP limit is full, so the user limit must not be charged either.
        self.assertFalse(recovery.reserve([(userLimit, 'u2'), (ipLimit, '1.1.1.1')]))
        self.assertEqual(AccountRecoveryAttempt.objects.filter(action='reset-user').count(), 1)

    def test_rejected_requests_add_no_rows(self):
        ipLimit = ('reset-ip', 1)
        self.assertTrue(recovery.reserve([(('reset-user', 3), 'first'), (ipLimit, '1.1.1.1')]))
        attempts = AccountRecoveryAttempt.objects.count()
        # A new username on every request, from an IP that is used up.
        for i in range(200):
            self.assertFalse(recovery.reserve([(('reset-user', 3), 'user%d' % i), (ipLimit, '1.1.1.1')]))
        self.assertEqual(AccountRecoveryAttempt.objects.count(), attempts)
        self.assertLessEqual(AccountRecoveryLock.objects.count(), recovery.LOCK_STRIPES)

    def test_old_rows_are_purged(self):
        from datetime import timedelta
        from django.utils import timezone
        old = timezone.now() - recovery.RETENTION - timedelta(minutes=1)
        AccountRecoveryAttempt.objects.create(action='reset-ip', keyHash='x' * 40, createdAt=old)
        self.assertTrue(recovery.reserve([(('reset-ip', 1), '2.2.2.2')]))
        self.assertFalse(AccountRecoveryAttempt.objects.filter(keyHash='x' * 40).exists())

    def test_retries_mysql_deadlock(self):
        from django.db import OperationalError
        real = recovery._reserveOnce
        calls = []
        def flaky(*args):
            calls.append(1)
            if len(calls) == 1:
                raise OperationalError(1213, 'Deadlock found when trying to get lock')
            return real(*args)
        recovery._reserveOnce = flaky
        try:
            self.assertTrue(recovery.reserve([(('reset-ip', 1), '3.3.3.3')]))
        finally:
            recovery._reserveOnce = real
        self.assertEqual(len(calls), 2)
        self.assertEqual(AccountRecoveryAttempt.objects.count(), 1)


class ClientIpTest(TestCase):
    def ip(self, remote, xff=None):
        from django.test import RequestFactory
        extra = {'REMOTE_ADDR': remote}
        if xff is not None:
            extra['HTTP_X_FORWARDED_FOR'] = xff
        return recovery.clientIp(RequestFactory().get('/', **extra))

    def test_direct_connection_ignores_forwarded_header(self):
        self.assertEqual(self.ip('203.0.113.9', '198.51.100.1'), '203.0.113.9')

    def test_behind_load_balancer_uses_address_it_appended(self):
        # The client sent "198.51.100.1"; the load balancer (10.0.0.2) appended
        # the real address 203.0.113.9.
        self.assertEqual(self.ip('10.0.0.2', '198.51.100.1, 203.0.113.9'), '203.0.113.9')

    def test_spoofed_entries_change_nothing(self):
        for spoof in ['1.2.3.4', '5.6.7.8, 9.9.9.9', '10.1.1.1', 'garbage']:
            self.assertEqual(self.ip('10.0.0.2', spoof + ', 203.0.113.9'), '203.0.113.9')

    def test_all_internal(self):
        self.assertEqual(self.ip('10.0.0.2', '192.168.1.5'), '192.168.1.5')
        self.assertEqual(self.ip('127.0.0.1'), '127.0.0.1')

    def test_unparseable_hop_stops_the_walk(self):
        self.assertEqual(self.ip('10.0.0.2', '203.0.113.7, junk'), '10.0.0.2')

    def test_trusted_proxies_setting(self):
        from django.test import override_settings
        with override_settings(RECOVERY_TRUSTED_PROXIES=['10.0.0.0/8', '130.176.0.0/16']):
            # A CDN hop (130.176.x.x) in front of the load balancer.
            self.assertEqual(self.ip('10.0.0.2', '203.0.113.9, 130.176.4.4'), '203.0.113.9')
