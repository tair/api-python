from django.test import TestCase
from common.tests import ManualTest

class NullServiceTest(ManualTest, TestCase):
    path = "/nullservice/"
    testMethodStr = "running ./manage.py test nullservice.manualTests"