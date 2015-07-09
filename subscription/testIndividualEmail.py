#!/usr/bin/python
import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from django.core.mail import send_mail

def emailActivationCodes(**kwargs):
    listr = '<ul style="font-size: 16px; color: #b9ca32;">'
    for l in kwargs['accessCodes']:
	listr += "<li>"+l+"</li><br>"
    listr += "</ul>"
    with open('individualEmail.html', 'r,') as myfile:
        html_message = myfile.read() % (
					kwargs['partnerLogo'],
					kwargs['name'],
        				'TAIR',
       	 				listr,
            "https://google.com",
				        kwargs['subscriptionDescription'],
				        kwargs['institute'],
				        kwargs['subscriptionTerm'],
				        kwargs['subscriptionQuantity'],
				        kwargs['payment'],
				        kwargs['transactionId'],
				        """
			               		"""+kwargs['addr1']+""",<br>
			        	        """+kwargs['addr2']+""",<br>
			        	        """+kwargs['addr3']+"""<br>
				        """,
        )
    subject = kwargs['subject']
    from_email = kwargs['senderEmail']
    recipient_list = kwargs['recipientEmails']
    send_mail(subject=subject, from_email=from_email, recipient_list=recipient_list, html_message=html_message, message=None)


emailActivationCodes(**{
	"partnerLogo": 'https://s3-us-west-2.amazonaws.com/pw2-logo/logo2.gif',
	"name": 'John McLane',
	"accessCodes": ["123456", "987654"],
	"subscriptionDescription": "TAIR Subscription",
	"institute": "Tech Institute",
	"subscriptionTerm": '3 year',
	"subscriptionQuantity": '5',
	"price": "$99.99",
	"payment": "$99.99",
	"transactionId": "tok_9087",
	"addr1": "643 Bair Island Rd, Suite 403",
	"addr2": "Redwood City, CA",
	"addr3": "USA - 94063",
	"recipientEmails": ["azeem@getexp.com", "steve@getexp.com"],
	"senderEmail": "steve@getexp.com",
	"subject": 'Thank You For Subscribing'
})
