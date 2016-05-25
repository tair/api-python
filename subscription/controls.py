from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import stripe
from partner.models import SubscriptionTerm, Partner
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from serializers import SubscriptionSerializer
from party.models import Party

import datetime
from django.utils import timezone

import uuid

from django.core.mail import send_mail
import logging

from django.conf import settings

class SubscriptionControl():

    @staticmethod
    def createOrUpdateSubscription(partyId, partnerId, period):
        now = timezone.now()
        subscriptionSet = Subscription.objects \
                                      .all() \
                                      .filter(partyId=partyId) \
                                      .filter(partnerId=partnerId)
        if len(subscriptionSet) == 0:
            subscription = None
        else:
            subscription = subscriptionSet[0]

        transactionType = None
        transactionStartDate = None
        transactionEndDate = None
        
        if subscription == None:
            # case1: new subscription
            partyObj = Party.objects.get(partyId=partyId)
            partnerObj = Partner.objects.get(partnerId=partnerId)
            subscription = Subscription()
            subscription.partnerId = partnerObj
            subscription.partyId = partyObj
            subscription.startDate = now
            subscription.endDate = now+datetime.timedelta(days=period)

            transactionType = 'create'
            transactionStartDate = subscription.startDate
            transactionEndDate = subscription.endDate
        else:
            endDate = subscription.endDate
            if (endDate<now):
                # case2: expired subscription
                subscription.endDate = now + datetime.timedelta(days=period)
                transactionType = 'renew'
                transactionStartDate = now
                transactionEndDate = subscription.endDate
            else:
                # case3: active subscription
                subscription.endDate = endDate + datetime.timedelta(days=period)
                transactionType = 'renew'
                transactionStartDate = endDate
                transactionEndDate = subscription.endDate
        
        return (subscription, transactionType, transactionStartDate, transactionEndDate)

class PaymentControl():

    @staticmethod
    def tryCharge(secret_key, stripe_token, priceToCharge, chargeDescription, termId, quantity, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, vat):
        message = {}
        message['price'] = priceToCharge
        message['termId'] = termId
        message['quantity'] = quantity
        if not PaymentControl.validateCharge(priceToCharge, termId, quantity):
            message['message'] = "Charge validation error"
            #message['status'] = False //PW-120 vet we will return 400 instead - see SubscriptionsPayment post - i.e. the caller 
            return message
        
        stripe.api_key = secret_key
        charge = stripe.Charge.create(
            amount=int(priceToCharge*100), # stripe takes in cents; UI passes in dollars. multiply by 100 to convert.
            currency="usd",
            source=stripe_token,
            description=chargeDescription, #PW-248
            metadata = {'Email': emailAddress, 'Institute': institute, 'VAT': vat}
            )
        activationCodes = PaymentControl.postPaymentHandling(termId, quantity)
        emailInfo = PaymentControl.getEmailInfo(activationCodes, termId, quantity, priceToCharge, charge.id, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, vat)
        PaymentControl.emailReceipt(emailInfo)
        status = True
        message['activationCodes'] = activationCodes
        try:
            pass
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
            message['message'] = "Unexpected exception: %s" % (e)

        message['status'] = status
        return message

    @staticmethod
    def getEmailInfo(activationCodes, termId, quantity, payment, transactionId, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, vat):
        #PW-253 hardcode prod URLs for tair. 
        #   pros:HLP-47737, HLP-48801 and alike won't occur
        #   cons: 1) user won't be returnd to his starting point (the page where he was doing the suscribtion flom
        #         2) demo env will have prod URL in the subscription email
        # If it's not tair then urls values are TBD for now. 
        # Note, we can check partnerObj.partnerId insted of checking arabidopsis substring in redirect string to determine partner
        if "arabidopsis" in redirect:
            #if tair user is already logged in he will get to welcome page
            #if user is not logged-in welcome url will redirect user to login page and after login he'll get to welcome page
            loginURL = settings.TAIR_LOGIN_URL #".../jsp/community/welcome.jsp"
            registerURL = settings.TAIR_REGISTRATION_URL #".../community/abrc-new-register.faces"
        else: #TODO
            loginURL = settings.GIRI_LOGIN_URL #"TBD"
            registerURL = settings.GIRI_LOGIN_URL #"TBD"
            
        termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        partnerObj = termObj.partnerId
        name = firstname+" "+lastname
        institute = institute
        address = street
        city = city
        state = state
        country = country
        zipcode = zip
        senderEmail = "info@phoenixbioinformatics.org"
        recipientEmails = [email]
        payment = "%.2f" % float(payment)
        return {
            "partnerLogo": partnerObj.logoUri,
            "name": name,
            "partnerName": partnerObj.name,
            "accessCodes": activationCodes,
            # https://demoui.arabidopsis.org/#/contentaccess/login?partnerId=tair&redirect=https:%2F%2Fdemotair.arabidopsis.org%2Fjsp%2Fcommunity%2Fwelcome.jsp 
            # http://demotair.arabidopsis.org/jsp/community/welcome.jsp
            #"loginUrl": hostname+"/#/login?partnerId="+partnerObj.partnerId+"&redirect="+redirect,
            "loginUrl": loginURL,
            "registerUrl": registerURL,
            "partnerId": partnerObj.partnerId,
            "subscriptionDescription": "%s Subscription" % partnerObj.name,
            "institute": institute,
            "subscriptionTerm": termObj.description,
            "subscriptionQuantity": quantity,
            "payment": payment,
            "transactionId": transactionId,
            "vat": vat,
            "addr1": "Phoenix Bioinformatics Corporation",
            "addr2": "643 Bair Island Road Suite 403",
            "addr3": "Redwood City, CA 94063",
            "recipientEmails": recipientEmails,
            "senderEmail": senderEmail,
            "subject":"Thank You For Subscribing",
        }

    @staticmethod
    def emailReceipt(emailInfo):
        kwargs = emailInfo
        listr = '<ul style="font-size: 16px; color: #b9ca32; font-family: Arial, Helvetica, sans-serif; -webkit-font-smoothing: antialiased;">'
        for l in kwargs['accessCodes']:
            listr += "<li>"+l+"</li><br>"
        listr += "</ul>"

        import os
        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, 'individualEmail.html')
        with open(file_path, 'r,') as myfile:
            html_message = myfile.read() % (
                kwargs['partnerLogo'],
                kwargs['name'],
                kwargs['partnerName'],
                listr,
                kwargs['loginUrl'],
                kwargs['partnerName'],
                kwargs['partnerName'],
                kwargs['registerUrl'],
                kwargs['subscriptionDescription'],
                kwargs['institute'],
                kwargs['subscriptionTerm'],
                kwargs['subscriptionQuantity'],
                kwargs['payment'],
                kwargs['transactionId'],
                kwargs['vat'],
                """
                """+kwargs['addr1']+""",<br>
                """+kwargs['addr2']+""",<br>
                """+kwargs['addr3']+"""<br>
                """)
        subject = kwargs['subject']
        from_email = kwargs['senderEmail']
        recipient_list = kwargs['recipientEmails']
#        logging.basicConfig(filename="/home/ec2-user/logs/debug.log",
#                            format='%(asctime)s %(message)s'
#        )
#        logging.error("------Sending individual email------")
#        logging.error("%s" % recipient_list[0])
        send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
#        logging.error("------Done sending individual email------")
        
    @staticmethod
    def isValidRequest(request, message):
        ret = True
        termId = request.GET.get('termId')
        quantity = request.GET.get('quantity')
        if termId==None:
            message['message']='error: no termId'
            ret = False
        elif PaymentControl.getTermPrice(termId)==None:
            message['message']='error: unable to get term price'
            ret = False
        elif quantity == None:
            message['message']='error: no quantity specified'
            ret = False
        elif int(quantity) < 1 or int(quantity) > 99:
            message['message']='error: quantity must be between 1 and 99'
            ret = False
        return ret

    @staticmethod
    def getTermPrice(termId):
        try:
            return float(SubscriptionTerm.objects.get(subscriptionTermId=termId).price)
        except:
            return None

    @staticmethod
    def postPaymentHandling(termId, quantity):
        if quantity > 99:
            return []
        termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        period = termObj.period
        partnerObj = termObj.partnerId
        partnerId = partnerObj.partnerId
        now = timezone.now()

        codeArray = []

        for i in xrange(quantity):
            # create an activation code based on partnerId and period.
            activationCodeObj = ActivationCode()
            activationCodeObj.activationCode=str(uuid.uuid4())
            activationCodeObj.partnerId=partnerObj
            activationCodeObj.period=period
            activationCodeObj.partyId=None
            activationCodeObj.purchaseDate=now
            activationCodeObj.save()
            codeArray.append(activationCodeObj.activationCode)

        return codeArray
    
    @staticmethod
    def validateCharge(price, termId, quantity):
        so = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        calcprice = so.price*quantity
        if so.groupDiscountPercentage > 0 and quantity > 1:
            calcprice = so.price*quantity*(1-(so.groupDiscountPercentage/100))
        calcprice = round(calcprice*100)/100
	return (price == calcprice)
