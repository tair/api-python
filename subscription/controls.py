from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import stripe
from partner.models import SubscriptionTerm
from subscription.models import Subscription, SubscriptionTransaction
from serializers import SubscriptionSerializer
from party.models import Party

import datetime
from django.utils import timezone

class PaymentControl():
    stripe_api_secret_test_key = "sk_test_dXy85QkwH66s64bIWKbikyMt"

    @staticmethod
    def tryCharge(secret_key, stripe_token, priceToCharge, chargeDescription, partyId, termId):
        message = {}
        message['price'] = priceToCharge
        message['partyId'] = partyId
        message['termId'] = termId
        stripe.api_key = secret_key
        try:
            charge = stripe.Charge.create(
                amount=priceToCharge,
                currency="usd",
                source=stripe_token,
                description=chargeDescription,
            )
            PaymentControl.postPaymentSubscription(termId, partyId)
            status = True
            message['message'] = "Thanks! Your card has been charged"
        except stripe.error.InvalidRequestError, e:
            status = False
            message['message'] = e.json_body['error']['message']
        except stripe.error.CardError, e:
            status = False
            message['message'] = e.json_body['error']['message']
        except stripe.error.AuthenticationError, e:
            status = False
            message['message'] = e.json_body['error']['message']
        except stripe.error.APIConnectionError, e:
            status = False
            message['message'] = e.json_body['error']['message']
        except Exception, e:
            status = False
            message['message'] = "Unexpected exception: %s %s" % (e, partyId)
        return status, message

    @staticmethod
    def isValidRequest(request, message):
        ret = True
        termId = request.GET.get('termId', '')
        if termId=='':
            message['message']='error: no termId'
            ret = False
        elif PaymentControl.getTermPrice(termId)==None:
            message['message']='error: unable to get term price'
            ret = False
        partyId = request.GET.get('partyId', '')
        if partyId=='':
            message['message']='error: no partyId'
            ret = False
        return ret

    @staticmethod
    def getTermPrice(termId):
        try:
            return int(SubscriptionTerm.objects.get(subscriptionTermId=termId).price)
        except:
            return None

    @staticmethod
    def postPaymentSubscription(termId, partyId):
        termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        partyObj = Party.objects.get(partyId=partyId)        
        period = termObj.period

        partnerObj = termObj.partnerId
        partnerId = partnerObj.partnerId

        now = timezone.now()
        subscriptionSet = Subscription.objects \
                                      .all() \
                                      .filter(partyId=partyId) \
                                      .filter(partnerId=partnerId)
        if len(subscriptionSet) == 0:
            subscription = None
        else:
            subscription = subscriptionSet[0]

        transactionType = 'Initial'
        if subscription == None:
            # new subscription
            subscription = Subscription()
            subscription.partnerId = partnerObj
            subscription.partyId = partyObj
            subscription.startDate = now
            subscription.endDate = now+datetime.timedelta(days=period)
        else:
            # already has a subscription
            endDate = subscription.endDate
            if (endDate>now):
                subscription.endDate = endDate + datetime.timedelta(days=period)
                # subscription still active, extend
                transactionType = 'Renew'
            else:
                subscription.endDate = now + datetime.timedelta(days=period)
                transactionType = 'Renew'

        subscription.save()
        subscriptionId = subscription.subscriptionId
        subscriptionTransactionId = SubscriptionTransaction.createFromSubscription(subscription, transactionType).subscriptionTransactionId

        return (subscriptionId, subscriptionTransactionId)

