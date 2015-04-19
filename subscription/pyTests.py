#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from unittest import TestCase
import unittest
from subscription.models import SubscriptionTerm as Term 
from subscription.models import Subscription, Party, Payment
from django.db import models
import django
import requests
import json
import sys, getopt

# Create your tests here.
django.setup()

try:
    opts, args = getopt.getopt(sys.argv[1:], "h:" , ["host="])
except getopt.GetoptError:
    print "Usage: python -m metering.pyTests --host <hostname>\n\rExample hostname: 'http://52.4.81.100:8080/'"
    sys.exit(1)

serverUrl = ""
for opt, arg in opts:
    if opt=='--host' or opt=='-h':
        serverUrl = arg

if serverUrl=="":
    print "hostname is required"
    sys.exit(1)


testTerm = {
    'period': "2015T5",
    'price': 50.0,
    'groupDiscountPercentage': 3.5,
    'autoRenew': False
}

testSubscription = {
    'startDate': "2000-01-01T00:00:00Z",
    'endDate': "2012-12-21T00:00:00Z"
}

toDelete = []
toDeleteParty = []
toDeleteSubscription = []

print "Running unit tests on subscription web services API........."

class SubscriptionTermTest(TestCase):
    def test_for_createTerm(self):
        req = requests.post(serverUrl+'subscriptions/terms/', data=testTerm)
        toDelete.append(req.json()['subscriptionTermId'])
        self.assertEqual(req.status_code, 201)
        self.assertIsNotNone(forceGetSubscriptionTerm(req.json()['subscriptionTermId']))
        forceDeleteSubscriptionTerm(req.json()['subscriptionTermId'])
    
    def test_for_getAllTerms(self):
        termId = forcePostSubscriptionTerm(testTerm)
        req = requests.get(serverUrl+'subscriptions/terms/')
        toDelete.append(termId)
        self.assertEqual(req.status_code, 200)
        forceDeleteSubscriptionTerm(termId)
 
    def test_for_updateTerm(self):
        termId = forcePostSubscriptionTerm(testTerm)
        data = {
            'period': "2016T5",
            'price': "6.5",
            'groupDiscountPercentage': "2.6",
            'autoRenew': "True"
        }
        req = requests.put(serverUrl+'subscriptions/terms/'+str(termId)+'/', data=data)
        toDelete.append(termId)
        self.assertEqual(req.status_code, 201)
        forceDeleteSubscriptionTerm(termId)
 
    def test_for_deleteTerm(self):
        termId = forcePostSubscriptionTerm(testTerm)
        req = requests.delete(serverUrl+'subscriptions/terms/'+str(termId))
        toDelete.append(termId)
        self.assertIsNone(forceGetSubscriptionTerm(termId))
 
    def test_for_getTerm(self):
        termId = forcePostSubscriptionTerm(testTerm)
        req = requests.get(serverUrl+'subscriptions/terms/'+str(termId))
        toDelete.append(termId)
        self.assertEqual(req.status_code, 200)
        forceDeleteSubscriptionTerm(termId)

    #TO-DO
    def test_for_queryTerm(self):
        pass

    def tearDown(self):
        for d in toDelete:
            forceDeleteSubscriptionTerm(d)
       

class SubscriptionTest(TestCase):
    def setUp(self):
        toDeleteParty = []
        toDeleteSubscription = []

    def test_for_getAllSubscriptions(self):
        partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        forcePostSubscription(testSubscription, partyId, termId)
        req = requests.get(serverUrl+'subscriptions/')
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)
        self.assertEqual(req.status_code, 200)
        #forceDeleteParty(partyId)
        #forceDeleteSubscriptionTerm(termId)

    def test_for_getSubscription(self):
        partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        forcePostSubscription(testSubscription, partyId, termId)
        req = requests.get(serverUrl+'subscriptions/'+str(partyId)+'/')
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)
        self.assertEqual(req.status_code, 200)
        #forceDeleteParty(partyId)
        #forceDeleteSubscriptionTerm(termId)

    def test_for_createSubscription(self):
	partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        data = {
            'partyId': partyId,
            'subscriptionTermId': termId,
            'startDate': "2000-01-01T00:00:00Z",
            'endDate': "2000-01-01T00:00:00Z"
        }
        req = requests.post(serverUrl+'subscriptions/', data=data)
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)    
        self.assertEqual(req.status_code, 201)

    def test_for_updateSubscription(self):
        partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        forcePostSubscription(testSubscription, partyId, termId)
        data = {'endDate': "2049-01-01T00:00:00Z"}
        req = requests.put(serverUrl+'subscriptions/'+str(partyId)+'/', data=data)
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)
        self.assertEqual(req.status_code, 201)
        

    def test_for_deleteSubscription(self):
        partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        forcePostSubscription(testSubscription, partyId, termId)
        req = requests.delete(serverUrl+'subscriptions/'+str(partyId))
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)
        self.assertEqual(req.status_code, 204)

    def test_for_querySubscription(self):
        pass

    def tearDown(self):
        for i in toDeleteParty:
            forceDeleteParty(i)
        for i in toDeleteSubscription:
            forceDeleteSubscriptionTerm(i)

class PaymentTest(TestCase):
    def setUp(self):
        toDeleteParty = []
        toDeleteSubscription = []

    def test_for_getAllPayment(self):
        partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        u = forcePostSubscription(testSubscription, partyId, termId)
        forcePostPayment(u)
        req = requests.get(serverUrl+'payments/')
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)
        self.assertEqual(req.status_code, 200)

    def test_for_postPayment(self):
        pass

    def test_for_getPayment(self):
        partyId = forcePostParty()
        termId = forcePostSubscriptionTerm(testTerm)
        u = forcePostSubscription(testSubscription, partyId, termId)
        forcePostPayment(u)
        req = requests.get(serverUrl+'payments/'+str(partyID))
        toDeleteParty.append(partyId)
        toDeleteSubscription.append(termId)
        self.assertEqual(req.status_code, 200)

    def test_for_updatePayment(self):
        pass
  
    def test_for_deletePayment(self):
        pass

    def tearDown(self):
        for i in toDeleteParty:
            forceDeleteParty(i)

 
#Auxillary functions
def forceGetSubscriptionTerm(termId):
    try:
        return Term.objects.get(subscriptionTermId=termId)
    except:
        return None

def forcePostSubscriptionTerm(term):
    u = Term(period=term['period'],
             price=term['price'],
             groupDiscountPercentage=term['groupDiscountPercentage'],
             autoRenew=term['autoRenew'])
    u.save()
    return u.subscriptionTermId


def forceDeleteSubscriptionTerm(termId):
    try:
        Term.objects.get(subscriptionTermId=termId).delete()
    except:
        pass

def forcePostParty():
    u = Party()
    u.save()
    return u.partyId

def forcePostSubscription(subscription, partyId, termId):
    try:
        return Subscription.objects.get(partyId=partyId, termId=termId)
    except:
        u = Subscription(partyId=Party.objects.get(partyId=partyId), 
                     subscriptionTermId=Term.objects.get(subscriptionTermId=termId), 
                     startDate=subscription['startDate'],
                     endDate=subscription['endDate'])
        u.save()
        return u

def forceDeleteParty(partyId):
    try:
        Party.objects.get(partyId=partyId).delete()
    except:
        pass

def forcePostPayment(partyId):
    u = Payment(partyId=partyId)
    u.save()
    return u.paymentId

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
