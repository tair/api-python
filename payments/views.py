#TODO: Currently this is called from /payments, integrate to /subscriptions

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import stripe
from subscription.models import SubscriptionTerm as Term
from subscription.models import Subscription, Payment
#import paypalrestsdk
import datetime

# Create your views here.
stripe_api_secret_test_key = "sk_test_dXy85QkwH66s64bIWKbikyMt"

def paymentInfo(request):
  message = {}
  if request.method == 'GET':
    if (not isValidRequest(request)):
      return HttpResponse("Bad request - bad term or party ID", 400)
    termId=request.GET.get('termId')
    partyId=request.GET.get('partyId')
    #Currently assumes that subscription objects in database stores price in cents
    #TODO: Handle more human readable price
    price = getTermPrice(termId)
    message['price'] = price
    message['partyId'] = partyId
    message['termId'] = termId

  if request.method == 'POST':
    stripe.api_key = stripe_api_secret_test_key
    token = request.POST['stripeToken']
    price = int(request.POST['price'])
    partyId = request.POST['partyId']
    termId = request.POST['termId']
    description = "Test charge"
    status, message = tryCharge(stripe_api_secret_test_key, token, price, description, partyId, termId)
    if status:
      return HttpResponse(message['message'], 201)

  return render(request, "payments/paymentIndex.html", message)

def getTermPrice(termId):
  try:
    return int(Term.objects.get(subscriptionTermId=termId).price)
  except:
    return None

def getSubscription(partyId):
  try:
    return Subscription.objects.get(partyId=partyId)
  except:
    return None

def isValidRequest(request):
  ret = True
  termId = request.GET.get('termId', '')
  if termId=='':
    ret = False
  elif getTermPrice(termId)==None:
    ret = False
  partyId = request.GET.get('partyId', '')
  if partyId=='':
    ret = False
  elif getSubscription(partyId)==None:
    ret = False
  return ret

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
    subscription = getSubscription(partyId)
    period = Term.objects.get(subscriptionTermId=termId).period
    endDate = subscription.endDate
    now = timezone.now()

    #TODO: Add period correctly
    if (endDate>now):
      subscription.endDate = endDate + datetime.timedelta(days=180)
    else:
      subscription.endDate = now + datetime.timedelta(days=180)
    subscription.save()
    Payment(partyId=subscription).save()
    status = True
    message['message'] = "Thanks! Your card has been charged authorized" 
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
    message['message'] = "Unexpected exception"
  return status, message

