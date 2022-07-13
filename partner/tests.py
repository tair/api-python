#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  
import sys
import django
import unittest
import copy
import json
from django.test import TestCase, Client
from partner.models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
from common.tests import TestGenericInterfaces, GenericCRUDTest, GenericGETOnlyTest, checkMatch
from .testSamples import PartnerSample, PartnerPatternSample, SubscriptionTermSample, SubscriptionDescriptionSample, SubscriptionDescriptionItemSample

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# test for API end point /partners/
class PartnerCRUD(GenericGETOnlyTest, TestCase):
    sample = PartnerSample(serverUrl)

# test for API end point /partners/patterns/
class PartnerPatternCRUD(GenericCRUDTest, TestCase):
    sample = PartnerPatternSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(PartnerPatternCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

    # cannot perform get all since for GET action sourceUri is required
    def test_for_get_all(self):
        pass

    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % ('sourceUri', sample.data['sourceUri'])

        # no cookie needed
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.data, json.loads(res.content), sample.pkName, pk), True)


# test for API end point /partners/terms/
class SubscriptionTermCRUD(GenericGETOnlyTest, TestCase):
    sample = SubscriptionTermSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(SubscriptionTermCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

# test for API end point /partners/descriptions/
# TODO: test for case when GET request is sent with includeText param
class SubscriptionDescriptionCRUD(GenericGETOnlyTest, TestCase):
    sample = SubscriptionDescriptionSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(SubscriptionDescriptionCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

# test for API end point /partners/descriptionItems/
class SubscriptionDescriptionItemCRUD(GenericCRUDTest, TestCase):
    sample = SubscriptionDescriptionItemSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    descriptionSample = SubscriptionDescriptionSample(serverUrl)

    def setUp(self):
        super(SubscriptionDescriptionItemCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.descriptionSample.data['partnerId']=self.partnerId
        self.descriptionId = self.descriptionSample.forcePost(self.descriptionSample.data)
        self.sample.data['subscriptionDescriptionId']=self.sample.updateData['subscriptionDescriptionId']=self.descriptionId

print("Running unit tests on partner web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
