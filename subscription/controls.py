import stripe
import uuid
from datetime import timedelta
import pytz
from dateutil.parser import parse
import time
import string
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from partner.models import SubscriptionTerm, Partner
from authentication.models import Credential
from subscription.models import *
from serializers import SubscriptionSerializer
from party.models import Party
from django.utils import timezone
from django.core.mail import send_mail
from common.utils.cipresUtils import APICaller
from common.utils.cyverseUtils import CyVerseClient

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
            subscription.endDate = now + timedelta(days=period)

            transactionType = 'create'
            transactionStartDate = subscription.startDate
            transactionEndDate = subscription.endDate
        else:
            endDate = subscription.endDate
            if (endDate<now):
                # case2: expired subscription
                subscription.endDate = now + timedelta(days=period)
                transactionType = 'renew'
                transactionStartDate = now
                transactionEndDate = subscription.endDate
            else:
                # case3: active subscription
                subscription.endDate = endDate + timedelta(days=period)
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
            try:
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
            except stripe.error.CardError as e:
                # Handle CardError specifically for customer creation
                message['message'] = "Card declined: %s" % (e.user_message)
                loggingMsg = "Card declined during customer creation: %s" % (e.user_message)
                PaymentControl.logPaymentError(partyId, userIdentifier, emailAddress, loggingMsg)
                return message
            except Exception, e:
                message['message'] = "Unexpected exception: %s" % (e)
                PaymentControl.logPaymentError(partyId, userIdentifier, emailAddress, message['message'])
                return message
        except stripe.error.CardError as e:
            # Handle CardError for customer modification
            message['message'] = "Card declined: %s" % (e.user_message)
            loggingMsg = "Card declined during customer modification: %s" % (e.user_message)
            PaymentControl.logPaymentError(partyId, userIdentifier, emailAddress, loggingMsg)
            return message
        except Exception, e:
            message['message'] = "Unexpected exception: %s" % (e)
            PaymentControl.logPaymentError(partyId, userIdentifier, emailAddress, message['message'])
            return message

        invoice_item = stripe.InvoiceItem.create(
            customer=customer.id,
            unit_amount= int(priceToCharge) * 100,
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

        status = True
        try:
            invoice=stripe.Invoice.create(
                customer=customer.id,
                description = chargeDescription,
                custom_fields = custom_fields,
            )
            invoice = stripe.Invoice.pay(invoice.id)
            logger.debug("Payment to stripe for CIPRES successfuly: " + invoice.id)
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
                    # do not put error message to response since the payment already gets through, it's just the sync failure
                    msg = "Your order has been processed, and the purchased CPU hours will be reflected in your CIPRES account within 24 hours."
                    PaymentControl.sendCIPRESSyncFailedEmail(purchaseId, transactionId, purchaseDate, userIdentifier, unitQty, postUnitPurchasePostResponse.status_code, postUnitPurchasePostResponse.text)
                    PaymentControl.sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, other)
            except Exception, e:
                # do not put error message to response since the payment already gets through, it's just the sync failure
                msg = "Your order has been processed, and the purchased CPU hours will be reflected in your CIPRES account within 24 hours."
                errorMsg = "Unexpected exception: %s" % (e)
                PaymentControl.sendCIPRESSyncFailedEmail(purchaseId, transactionId, purchaseDate, userIdentifier, unitQty, "N/A", errorMsg)
                PaymentControl.sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, other)

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
        category = termObj.category
        category_cap = category[0].capitalize() + category[1:]
        description = category_cap + " | " + termObj.description

        html_message = partnerObj.activationEmailInstructionText % (
            partnerObj.logoUri,
            name,
            msg,
            institute,
            description,
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
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
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
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, message=msg)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
        logger.info("------Done sending email------")


    @staticmethod
    def chargeForCyVerse(stripe_api_key, stripe_token, priceToCharge, subscription, username, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, cardLast4, other, domain):
        message = {}
        message['price'] = priceToCharge
        partnerId = "cyverse" # hard code until other partner adopts the same model
        stripeDescription = PaymentControl.createCyVerseStripeDescription(subscription, other, firstname, lastname)
        status = True
        #display error boolean for error capturing 
        displayError = False
        errMsg = ''
        charge_amount = int(priceToCharge*100)# stripe takes in cents; UI passes in dollars. multiply by 100 to convert.

        try:
            partyObj = Credential.getByUsernameAndPartner(username, partnerId).partyId
            partyId = partyObj.partyId
        except Credential.DoesNotExist:
            status = False
            message['message'] = "Cannot find user %s for partner %s" % (username, partnerId)
            errMsg = message['message']
            partyId = "Cannot find"
        except Credential.MultipleObjectsReturned:
            #get the first username from the list if there are duplicates and set the party ID
            partyObj = Credential.getFirstByUsernameAndPartner(username, partnerId).partyId
            partyId = partyObj.partyId
            errMsg = "Find more than one user %s for partner %s" % (username, partnerId)
            PaymentControl.sendCyVersePaymentErrorEmail(username, charge_amount, errMsg)

        message['status'] = status

        if status:
            try:
                stripe.api_key = stripe_api_key
                charge = stripe.Charge.create(
                    amount = charge_amount,
                    currency="usd",
                    source=stripe_token,
                    description=stripeDescription,
                    metadata = {'Email': emailAddress, 'Institute': institute, 'Other': other}
                )
                pass
            except stripe.error.InvalidRequestError, e:
                status = False
                displayError = True
                message['message'] = e.json_body['error']['message']
                errMsg = message['message']
            except stripe.error.CardError, e:
                status = False
                displayError = True
                message['message'] = e.json_body['error']['message']
                errMsg = message['message']
            except stripe.error.AuthenticationError, e:
                status = False
                message['message'] = e.json_body['error']['message']
                errMsg = message['message']
            except stripe.error.APIConnectionError, e:
                status = False
                message['message'] = e.json_body['error']['message']
                errMsg = message['message']
            except Exception, e:
                status = False
                message['message'] = "Unexpected exception: %s" % (e)
                errMsg = message['message']

        #capture any changes in whether an error that should be displayed or not
        message['displayError'] = displayError

        if status:
            transactionId = charge.id
            purchaseDate = timezone.now()
            client = CyVerseClient()
            termLabel = 'N/A'
            addOnDescription = 'N/A'
            subscriptionUUID = ''
            expirationDate = ''
            syncStatus = True
            # test for invalid user. Note that API does not return error for invalid username

            if 'subscription' in subscription:
                tierId = subscription['subscription']['tierId']
                termObj = UsageTierTerm.objects.get(tierId=tierId)
                partnerObj = termObj.partnerId
                durationInDays = termObj.durationInDays
                tierPurchaseObj = PaymentControl.createUsageTierPurchase(partyObj, partnerObj, termObj, purchaseDate, transactionId);
                purchaseId = tierPurchaseObj.purchaseId
                expirationDate = tierPurchaseObj.expirationDate
                termName = termObj.name
                termLabel = termObj.label
                cyverseSubscription = client.getSubscriptionTier(username)
                currentExpiration = cyverseSubscription['endDate']
                # if currentExpiration is today or before today, we need to create a flag called renewal set to false
                # this is because if the currentExpiration is a future date, that means this is a renewal purchase
                now = timezone.now()
                current_expiration_date = parse(currentExpiration).replace(tzinfo=pytz.UTC)
                renewal = current_expiration_date > now and current_expiration_date < (now + timedelta(days=30))

                if termLabel:
                    termLabel = string.capwords(termLabel)

                try:
                    client.postTierPurchase(username, termName, durationInDays, currentExpiration, renewal=renewal)
                    cyverseSubscription = client.getSubscriptionTier(username)
                    if (cyverseSubscription['tier'] != termName and not renewal):
                        raise RuntimeError("CyVerse tier name %s and local tier name %s does not match" % (cyverseSubscription['tier'], termName))
                    tierPurchaseObj.partnerUUID = cyverseSubscription['uuid']

                    # Calculate expiration date based on renewal status
                    if not renewal:
                        expirationDate = cyverseSubscription['endDate']
                    else:
                        current_expiration = cyverseSubscription['endDate']
                        current_expiration_date = parse(current_expiration).replace(tzinfo=pytz.UTC)
                        expirationDate = (current_expiration_date + timedelta(days=durationInDays + 1)).strftime("%Y-%m-%d")
                    
                    tierPurchaseObj.expirationDate = expirationDate
                    subscriptionUUID = cyverseSubscription['uuid']
                    # expirationDate = cyverseSubscription['endDate']
                    tierPurchaseObj.syncedToPartner = True
                    tierPurchaseObj.save()
                except RuntimeError as error:
                    syncStatus = False
                    message['message'] = error
                    errMsg = message['message']

            if 'addons' in subscription:
                addOnDescription = ''
                for addOnPurchase in subscription['addons']:
                    optionId = addOnPurchase['optionId']
                    qty = addOnPurchase['purchaseQty']
                    if not subscriptionUUID:
                        subscriptionUUID = addOnPurchase['subscriptionUUID']
                    if not expirationDate:
                        expirationDate = addOnPurchase['expirationDate']
                    chargeAmount = addOnPurchase['chargeAmount']
                    optionObj = UsageAddonOption.objects.get(optionId=optionId)
                    partnerObj = optionObj.partnerId
                    addOnPurchaseObj = PaymentControl.createAddonPurchase(partyObj, partnerObj, optionObj, purchaseDate, transactionId, qty, subscriptionUUID, expirationDate, chargeAmount)
                    if (qty > 1):
                        addOnDescription += '%s * %s;' % (optionObj.name, qty)
                    else:
                        addOnDescription += optionObj.name

                    try:
                        PaymentControl.postAddonPurchase(addOnPurchaseObj, client)
                    except RuntimeError as error:
                        syncStatus = False
                        message['message'] = error
                        errMsg = message['message']

            if syncStatus:
                msg = "Your order has been processed and your CyVerse account has been credited."
                PaymentControl.sendCyVerseAdminEmail(termLabel, addOnDescription, username, purchaseDate, transactionId)
            else:
                msg = "Your order has been processed, and your CyVerse account will be credited within 48 hours."
                PaymentControl.sendCyVerseSyncFailedEmail(termLabel, addOnDescription, username, purchaseDate, transactionId, errMsg)

            PaymentControl.sendCyVerseEmail(msg, username, termLabel, addOnDescription, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, expirationDate, cardLast4, other)
        else:
            #Covers the payment failure case
            PaymentControl.sendCyVersePaymentErrorEmail(username, charge_amount, errMsg)

        if errMsg:
            PaymentControl.logPaymentError(partyId, username, emailAddress, errMsg)

        return message

    @staticmethod
    def createCyVerseStripeDescription(subscription, other, firstname, lastname):
        stripeDescription = "CyVerse"
        if 'subscription' in subscription:
            tierId = subscription['subscription']['tierId']
            termObj = UsageTierTerm.objects.get(tierId=tierId)
            stripeDescription += " %s subscription ($%s USD)" % (termObj.name, termObj.price)

        if 'addons' in subscription:
            for addOnPurchase in subscription['addons']:
                optionId = addOnPurchase['optionId']
                amountPaid = addOnPurchase['chargeAmount']
                optionName = UsageAddonOption.objects.get(optionId=optionId).name
                qty = addOnPurchase['purchaseQty']
                stripeDescription += " %s add on options * %s ($%s USD)" % (optionName, qty, amountPaid)

        stripeDescription += 'other info: %s name: %s %s' % (other,firstname,lastname)
        return stripeDescription

    @staticmethod
    def postAddonPurchase(addOnPurchaseObj, client):
        subscriptionUUID = addOnPurchaseObj.partnerSubscriptionUUID
        optionUUID = addOnPurchaseObj.optionId.partnerUUID
        for i in range(addOnPurchaseObj.optionItemQty):
            addOnPurchaseSync = UsageAddonPurchaseSync()
            addOnPurchaseSync.purchaseId = addOnPurchaseObj
            try:
                uuid = client.postAddonPurchase(subscriptionUUID, optionUUID)
                addOnPurchaseSync.partnerUUID = uuid
                addOnPurchaseSync.save()
            except RuntimeError as error:
                raise 

    @staticmethod
    def createUsageTierPurchase(partyId, partnerId, termObj, purchaseDate, transactionId):
        tierPurchaseObj = UsageTierPurchase()
        tierPurchaseObj.partnerId=partnerId
        tierPurchaseObj.partyId=partyId
        tierPurchaseObj.tierId=termObj
        tierPurchaseObj.purchaseDate=purchaseDate
        tierPurchaseObj.expirationDate = PaymentControl.getExpirationDate(purchaseDate, termObj.durationInDays)
        tierPurchaseObj.transactionId=transactionId
        tierPurchaseObj.syncedToPartner=False
        tierPurchaseObj.save()

        return tierPurchaseObj

    @staticmethod
    def createAddonPurchase(partyObj, partnerObj, optionObj, purchaseDate, transactionId, qty, subscriptionUUID, expirationDate, chargeAmount):
        addOnPurchaseObj = UsageAddonPurchase()
        addOnPurchaseObj.partnerId=partnerObj
        addOnPurchaseObj.partyId=partyObj
        addOnPurchaseObj.optionId=optionObj
        addOnPurchaseObj.partnerSubscriptionUUID = subscriptionUUID
        addOnPurchaseObj.purchaseDate=purchaseDate
        addOnPurchaseObj.expirationDate = expirationDate
        addOnPurchaseObj.transactionId=transactionId
        addOnPurchaseObj.optionItemQty = qty
        addOnPurchaseObj.amountPaid = chargeAmount
        addOnPurchaseObj.save()

        return addOnPurchaseObj

    @staticmethod
    def getExpirationDate(purchaseDate, durationInDays):
        expirationDate = purchaseDate + timedelta(days=(durationInDays))
        return expirationDate.strftime("%Y-%m-%d 23:59:59")

    #send email to the tech team that a payment has failed
    @staticmethod
    def sendCyVersePaymentErrorEmail(username, charge_amount, errMsg):
        subject = "An error has occurred while a user was making a purchase"
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["techteam@arabidopsis.org"]
        msg = """
    Following user tried to create a purchase and got the error:
        username: %s
        amount: %s
        Error message: %s
        """ % (username, charge_amount, errMsg)
        logger.info("------Sending Phoenix Bioinformatics an email about failed purchase------")
        logger.info("Username: %s" % username)
        logger.info("Amount: %s" % charge_amount)
        logger.info("Error Message: %s" % errMsg)
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, message=msg)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
        logger.info("------Done sending email------")

    @staticmethod
    def sendCyVerseEmail(msg, username, termLabel, addOnDescription, partnerObj, email, firstname, lastname, payment, institute, transactionId, expirationDate, cardLast4, other):
        name = firstname + " " + lastname
        payment = "%.2f" % float(payment)

        # dt = parse(expirationDate)
        # gmt_timezone = pytz.timezone('Etc/GMT')
        # dt = dt.astimezone(gmt_timezone)
        # expirationDateDisplay = dt.strftime('%Y-%m-%d %H:%M %Z')

        dt = parse(expirationDate)
        if dt.tzinfo is None:  # Check if the datetime is naive
            # Assign a timezone to the naive datetime
            # Either use the local timezone:
            local_timezone = pytz.timezone('UTC')  # or whatever the source timezone should be
            dt = local_timezone.localize(dt)
            
        # Now convert to the target timezone
        gmt_timezone = pytz.timezone('Etc/GMT')
        dt = dt.astimezone(gmt_timezone)
        expirationDateDisplay = dt.strftime('%Y-%m-%d %H:%M %Z')

        html_message = partnerObj.activationEmailInstructionText % (
            partnerObj.logoUri,
            name,
            msg,
            institute,
            termLabel,
            addOnDescription,
            payment,
            transactionId,
            cardLast4,
            expirationDateDisplay,
            other,
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
        logger.info("Username: %s" % username)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Main Message: %s" % msg)
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
        logger.info("------Done sending email------")

    @staticmethod
    def sendCyVerseAdminEmail(termLabel, addOnDescription, username, purchaseDate, transactionId):
        subject = settings.CYVERSE_PURCHASE_EMAIL_SUBJECT
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = settings.CYVERSE_ADMINS

        msg = """
    CyVerse subscription purchased:
        Term: %s
        Add-on Options: %s
        Username: %s
        Transaction ID: %s
        Purchase Time: %s
        """ % (termLabel, addOnDescription, username, transactionId, purchaseDate)

        logger.info("------Sending CyVerse admin email------")
        logger.info("Term: %s" % termLabel)
        logger.info("Add-on Options: %s" % addOnDescription)
        logger.info("Username: %s" % username)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Subject: %s" % subject)
        logger.info("Message: %s" % msg)
        logger.info("recipients: %s" % recipient_list)
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, message=msg)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
        logger.info("------Done sending email------")

    @staticmethod
    def sendCyVerseSyncFailedEmail(termLabel, addOnDescription, username, purchaseDate, transactionId, error):
        subject = settings.CYVERSE_PURCHASE_EMAIL_SUBJECT
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = settings.CYVERSE_ADMINS

        msg = """
    CyVerse subscription purchased:
        Term: %s
        Add-on Options: %s
        Username: %s
        Transaction ID: %s
        Purchase Time: %s

    Failed to sync to the CyVerse database. Error message: %s
        """ % (termLabel, addOnDescription, username, transactionId, purchaseDate, error)

        logger.info("------Sending CyVerse sync failed email------")
        logger.info("Term: %s" % termLabel)
        logger.info("Add-on Options: %s" % addOnDescription)
        logger.info("Username: %s" % username)
        logger.info("Transaction ID: %s" % transactionId)
        logger.info("Subject: %s" % subject)
        logger.info("Message: %s" % msg)
        logger.info("Recipients: %s" % recipient_list)
        logger.info("Error Message: %s" % error)
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, message=msg)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
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
                metadata = {'Email': emailAddress, 'Institute': institute, 'Other': other}
                )
            activationCodes = PaymentControl.postPaymentHandling(termId, quantity)
            emailInfo = PaymentControl.getEmailInfo(activationCodes, partnerName, termId, quantity, priceToCharge, charge.id, emailAddress, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, other, domain)
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
        try:
            send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)
        except Exception, e:
            logger.info("Get Exception when sending the email: %s" % (e))
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
        return (price == calcprice or price == calcprice*0.9)
