import stripe
import uuid
import datetime
import time
import string
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from partner.models import SubscriptionTerm, Partner
from authentication.models import Credential
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode, UsageUnitPurchase, UsageTierTerm, UsageTierPurchase
from serializers import SubscriptionSerializer
from party.models import Party
from django.utils import timezone
from django.core.mail import send_mail
from common.utils.cipresUtils import APICaller

import logging
logger = logging.getLogger('phoenix.api.subscription')

from django.conf import settings

import urllib

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

    # for CIPRES credit purchase payment
    @staticmethod
    def chargeForCIPRES(partyId, userIdentifier, secret_key, stripe_token, priceToCharge, partnerName, chargeDescription, termId, quantity, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, other, domain):
        message = {}
        message['price'] = priceToCharge
        message['termId'] = termId
        message['quantity'] = quantity
        if not PaymentControl.validateCharge(priceToCharge, termId, quantity):
            message['message'] = "Charge validation error"
            PaymentControl.logPaymentError(partyId, userIdentifier, emailAddress, message['message'])
            #message['status'] = False //PW-120 vet we will return 400 instead - see SubscriptionsPayment post - i.e. the caller 
            return message
        
        stripe.api_key = secret_key
        try:
            customer = stripe.Customer.modify(
                'cus_' + partyId + '_' + userIdentifier + '_' + partnerName,
                name=firstname + lastname,
                email=emailAddress,
                address={
                  'line1': street,
                  'city': city,
                  'state': state,
                  'country': country,
                  'postal_code': zip
                },
                source=stripe_token,
                metadata={'Institution Name': institute},
            )
        except stripe.error.InvalidRequestError as e:
            customer = stripe.Customer.create(
                id='cus_' + partyId + '_' + userIdentifier + '_' + partnerName,
                name=firstname + lastname,
                email=emailAddress,
                address={
                    'line1': street,
                    'city': city,
                    'state': state,
                    'country': country,
                    'postal_code': zip
                },
                source=stripe_token,
                metadata={'Institution Name': institute},
            )

        invoice_item = stripe.InvoiceItem.create(
            customer=customer.id,
            unit_amount= int(SubscriptionTerm.objects.get(subscriptionTermId=termId).price) * 100,
            currency='usd',
            quantity=quantity,
            description=chargeDescription   #PW-248
        )
        custom_fields = [{
                'name': 'institution',
                'value': institute
            }]
        if other:
            custom_fields.append({
                'name': 'Other information',
                'value': other
            })
        invoice=stripe.Invoice.create(
            customer=customer.id,
            description = chargeDescription,
            custom_fields = custom_fields,
        )
        invoice = stripe.Invoice.pay(invoice.id)
        transactionId = invoice.charge
        stripe.PaymentIntent.modify(
            invoice.payment_intent,
            description = chargeDescription,
            metadata={
                'Email': emailAddress,
                'Institute': institute,
                'Other': other
            }
        )
        status = True
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
        
        if status:
            termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
            partnerObj = termObj.partnerId
            unitQty = termObj.period
            purchaseDate = timezone.now()

            partyObj = Party.objects.get(partyId=partyId)

            unitPurchaseObj = PaymentControl.createUnitPurchase(partyObj, partnerObj, unitQty, purchaseDate, transactionId);
            purchaseId = unitPurchaseObj.purchaseId

            caller = APICaller()
            try:
                postUnitPurchasePostResponse = caller.postUnitPurchase(userIdentifier, unitQty, transactionId, purchaseDate)
                
                if postUnitPurchasePostResponse.status_code == 201:
                    msg = "To access CIPRES resources, please visit phylo.org and log in using your CIPRES user account."
                    #PaymentControl.sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, other)
                    unitPurchaseObj.syncedToPartner = True
                    unitPurchaseObj.save()

                else:
                    msg = "Your order has been processed, and the purchased CPU hours will be reflected in your CIPRES account within 24 hours."
                    PaymentControl.sendCIPRESSyncFailedEmail(purchaseId, transactionId, purchaseDate, userIdentifier, unitQty, postUnitPurchasePostResponse.status_code, postUnitPurchasePostResponse.text)
                    PaymentControl.sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, other)
            except Exception, e:
                msg = "Your order has been processed, and the purchased CPU hours will be reflected in your CIPRES account within 24 hours."
                PaymentControl.sendCIPRESSyncFailedEmail(purchaseId, transactionId, purchaseDate, userIdentifier, unitQty, postUnitPurchasePostResponse.status_code, postUnitPurchasePostResponse.text)
                PaymentControl.sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, other)
                message['message'] = "Unexpected exception: %s" % (e)
            
        if 'message' in message:
            PaymentControl.logPaymentError(partyId, userIdentifier, emailAddress, message['message'])

        return message

    @staticmethod
    def logPaymentError(partyId, userIdentifier, emailAddress, message):
         logger.info("------Payment Charge Failed------")
         logger.info("User Party ID: %s" % partyId)
         logger.info("User Identifier: %s" % userIdentifier)
         logger.info("User Email for Purchase: %s" % emailAddress)
         logger.info("Error Message: %s" % message)
         logger.info("---------------------------------")

    @staticmethod
    def createUnitPurchase(partyId, partnerId, unitQty, purchaseDate, transactionId):
        unitPurchaseObj = UsageUnitPurchase()
        unitPurchaseObj.partnerId=partnerId
        unitPurchaseObj.quantity=unitQty
        unitPurchaseObj.purchaseDate=purchaseDate
        unitPurchaseObj.partyId=partyId
        unitPurchaseObj.transactionId=transactionId
        unitPurchaseObj.syncedToPartner=False
        unitPurchaseObj.save()

        return unitPurchaseObj

    @staticmethod
    def sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, email, firstname, lastname, payment, institute, transactionId, other):
        name = firstname + " " + lastname
        payment = "%.2f" % float(payment)
        
        html_message = partnerObj.activationEmailInstructionText % ( 
            partnerObj.logoUri,
            name,
            msg,
            institute,
            termObj.description,
            payment,
            transactionId,
            other,
            """
            Phoenix Bioinformatics Corporation<br>
            39899 Balentine Drive, Suite 200<br>
            Newark, CA, 94560, USA<br>
            """)
        
        subject = "Subscription Receipt"
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = [email]

        logger.info("------Sending CIPRES subscription email------")
        logger.info("Receipient: %s" % recipient_list[0])
        logger.info("Usage Unit Purchase ID: %s" % purchaseId)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Main Message: %s" % msg)
        send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
        logger.info("------Done sending email------")

    @staticmethod
    def sendCIPRESSyncFailedEmail(purchaseId, transactionId, purchaseDate, userIdentifier, unitQty, statusCode, error):
        subject = "Failed to sync CIPRES subscription"
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = settings.CIPRES_ADMINS

        msg = """
    Failed to sync CIPRES subscription to CIPRES database.
        HTTP status code: %s
        Error: %s
        Unit Purchase ID: %s
        Transaction ID: %s
        Purchase Time: %s
        User Identifier: %s
        Purchase Unit: %s
    Please address it ASAP.
        """ % (statusCode, error, purchaseId, transactionId, purchaseDate, userIdentifier, unitQty)

        logger.info("------Sending CIPRES sync failed email------")
        logger.info("Usage Unit Purchase ID: %s" % purchaseId)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Main Message: %s" % msg)
        send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, message=msg)
        logger.info("------Done sending email------")


    @staticmethod
    def chargeForCyVerse(stripe_api_key, stripe_token, priceToCharge, stripeDescription, username, partnerName, tierId, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, cardLast4, vat, domain):
        message = {}
        message['price'] = priceToCharge
        message['tierId'] = tierId
        termObj = UsageTierTerm.objects.get(tierId=tierId)
        partnerObj = termObj.partnerId
        partnerId = partnerObj.partnerId
        status = True

        try:
            partyObj = Credential.getByUsernameAndPartner(username, partnerId).partyId
            partyId = partyObj.partyId

            try:
                stripe.api_key = stripe_api_key
                charge = stripe.Charge.create(
                    amount=int(priceToCharge*100), # stripe takes in cents; UI passes in dollars. multiply by 100 to convert.
                    currency="usd",
                    source=stripe_token,
                    description=stripeDescription,
                    metadata = {'Email': emailAddress, 'Institute': institute, 'VAT': vat}
                )
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
        except Credential.DoesNotExist:
            status = False
            message['message'] = "Cannot find user %s for partner %s" % (username, partnerId)
            partyId = "Cannot find"
        except Credential.MultipleObjectsReturned:
            status = False
            message['message'] = "Find more than one user %s for partner %s" % (username, partnerId)
            partyId = "More than one"

        message['status'] = status
        
        if status:
            transactionId = charge.id
            purchaseDate = timezone.now()

            tierPurchaseObj = PaymentControl.createUsageTierPurchase(partyObj, partnerObj, termObj, purchaseDate, transactionId);
            purchaseId = tierPurchaseObj.purchaseId
            expirationDate = tierPurchaseObj.expirationDate

            termName = termObj.name
            if termName:
                termName = string.capwords(termName)

            # TODO: send to CyVerse API later
            msg = "Your order has been processed, and your CyVerse account will be credited within 48 hours."
            PaymentControl.sendCyVerseEmail(msg, purchaseId, termName, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, expirationDate, cardLast4, vat)
            PaymentControl.sendCyVerseAdminEmail(termName, username, purchaseDate, transactionId)
            tierPurchaseObj.syncedToPartner = True
            tierPurchaseObj.save()

        if 'message' in message:
            PaymentControl.logPaymentError(partyId, username, emailAddress, message['message'])

        return message

    @staticmethod
    def createUsageTierPurchase(partyId, partnerId, termObj, purchaseDate, transactionId):
        unitPurchaseObj = UsageTierPurchase()
        unitPurchaseObj.partnerId=partnerId
        unitPurchaseObj.partyId=partyId
        unitPurchaseObj.tierId=termObj
        unitPurchaseObj.purchaseDate=purchaseDate
        unitPurchaseObj.expirationDate = PaymentControl.getExpirationDate(purchaseDate, termObj.durationInDays)
        unitPurchaseObj.transactionId=transactionId
        unitPurchaseObj.syncedToPartner=False
        unitPurchaseObj.save()

        return unitPurchaseObj

    @staticmethod
    def getExpirationDate(purchaseDate, durationInDays):
        expirationDate = purchaseDate+datetime.timedelta(days=(durationInDays))
        return expirationDate.strftime("%Y-%m-%d 23:59:59")

    @staticmethod
    def sendCyVerseEmail(msg, purchaseId, termName, partnerObj, email, firstname, lastname, payment, institute, transactionId, expirationDate, cardLast4, vat):
        name = firstname + " " + lastname
        payment = "%.2f" % float(payment)
        expirationDateDisplay = expirationDate + " GMT"
        
        html_message = partnerObj.activationEmailInstructionText % ( 
            partnerObj.logoUri,
            name,
            msg,
            institute,
            termName,
            payment,
            transactionId,
            cardLast4,
            expirationDateDisplay,
            vat,
            """
            Phoenix Bioinformatics Corporation<br>
            39899 Balentine Drive, Suite 200<br>
            Newark, CA, 94560, USA<br>
            """)
        
        subject = "Subscription Receipt"
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = [email]

        logger.info("------Sending CyVerse subscription email------")
        logger.info("Receipient: %s" % recipient_list[0])
        logger.info("Subscription Tier Purchase ID: %s" % purchaseId)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Main Message: %s" % msg)
        send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
        logger.info("------Done sending email------")

    @staticmethod
    def sendCyVerseAdminEmail(termName, username, purchaseDate, transactionId):
        subject = settings.CYVERSE_PURCHASE_EMAIL_SUBJECT
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = settings.CYVERSE_ADMINS

        msg = """
    CyVerse subscription purchased:
        term: %s
        username: %s
        Transaction ID: %s
        Purchase Time: %s
        """ % (termName, username, transactionId, purchaseDate)

        logger.info("------Sending CyVerse admin email------")
        logger.info("Term: %s" % termName)
        logger.info("username: %s" % username)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Subject: %s" % subject)
        logger.info("Message: %s" % msg)
        logger.info("recipients: %s" % recipient_list)
        send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, message=msg)
        logger.info("------Done sending email------")

    # for regular Phoenix subscription payment
    @staticmethod
    def tryCharge(secret_key, stripe_token, priceToCharge, partnerName, chargeDescription, termId, quantity, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, other, domain):
        message = {}
        message['price'] = priceToCharge
        message['termId'] = termId
        message['quantity'] = quantity
        if not PaymentControl.validateCharge(priceToCharge, termId, quantity):
            message['message'] = "Charge validation error"
            #message['status'] = False //PW-120 vet we will return 400 instead - see SubscriptionsPayment post - i.e. the caller 
            return message
        try:
            stripe.api_key = secret_key
            charge = stripe.Charge.create(
                amount=int(priceToCharge*100), # stripe takes in cents; UI passes in dollars. multiply by 100 to convert.
                currency="usd",
                source=stripe_token,
                description=chargeDescription, #PW-248
                metadata = {'Email': emailAddress, 'Institute': institute, 'VAT': vat}
                )
            activationCodes = PaymentControl.postPaymentHandling(termId, quantity)
            emailInfo = PaymentControl.getEmailInfo(activationCodes, partnerName, termId, quantity, priceToCharge, charge.id, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, vat, domain)
            PaymentControl.emailReceipt(emailInfo, termId)
            status = True
            message['activationCodes'] = activationCodes
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
    def getEmailInfo(activationCodes, partnerName, termId, quantity, payment, transactionId, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, other, domain):
        
        termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        partnerObj = termObj.partnerId
        loginURL = domain + partnerObj.loginUri
        if partnerObj.defaultLoginRedirect is not None:
            param = "?redirect=" + urllib.quote(partnerObj.defaultLoginRedirect, safe='~')
            loginURL += param
        registerURL = partnerObj.registerUri
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
            "loginUrl": loginURL,
            "registerUrl": registerURL,
            "partnerId": partnerObj.partnerId,
            "subscriptionDescription": "%s Subscription" % partnerObj.name,
            "institute": institute,
            "subscriptionTerm": termObj.description,
            "subscriptionQuantity": quantity,
            "payment": payment,
            "transactionId": transactionId,
            "other": other,
            "addr1": "Phoenix Bioinformatics Corporation",
            "addr2": "39899 Balentine Drive, Suite 200",
            "addr3": "Newark, CA, 94560, USA",
            "recipientEmails": recipientEmails,
            "senderEmail": senderEmail,
            "subject":"Your %s Subscription Activation Code and Receipt" % partnerName,
        }

    @staticmethod
    def emailReceipt(emailInfo, termId):
        kwargs = emailInfo
        listr = '<ul style="font-size: 16px; color: #b9ca32; font-family: Arial, Helvetica, sans-serif; -webkit-font-smoothing: antialiased;">'
        for l in kwargs['accessCodes']:
            listr += "<li>"+l+"</li><br>"
        listr += "</ul>"

        termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        partnerObj = termObj.partnerId
        
        html_message = partnerObj.activationEmailInstructionText % ( 
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
                kwargs['other'],
                """
                """+kwargs['addr1']+""",<br>
                """+kwargs['addr2']+""",<br>
                """+kwargs['addr3']+"""<br>
                """)
        
        
        subject = kwargs['subject']
        from_email = kwargs['senderEmail']
        recipient_list = kwargs['recipientEmails']
        logger.info("------Sending activation code email------")
        logger.info("Receipient: %s" % recipient_list[0])
        logger.info("ActivationCodes:")
        for l in kwargs['accessCodes']:
            logger.info(l)
        send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
        logger.info("------Done sending activation code email------")
        
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
            activationCodeObj.transactionType='create'
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
