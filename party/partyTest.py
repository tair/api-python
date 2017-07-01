from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.test import APITestCase
import django

django.setup()
class AccountTests(APITestCase):
    def test_get_party(self):
        factory = APIRequestFactory()
        request = factory.get('/parties/')

        self.assertEqual(request.status_code, status.HTTP_200_OK)