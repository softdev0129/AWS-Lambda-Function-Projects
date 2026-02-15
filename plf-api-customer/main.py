import json
import firebase_admin
from firebase_admin import credentials
from auth.register import Register
from auth.login import Login
from auth.reset_password import ResetPassword
from auth.social_login import SocialLogin
from billing.check_billing import CheckBilling
from billing.paypal_subscription import ProcessPaypalSubscription
from customer.get_user_profile import GetUserProfile
from customer.get_locale import get_location_info
from customer.get_provider import GetProvider
from customer.contactus import ContactUs
import os

from billing.buy_subscription import BuySubscription
from billing.cancel_subscription import CancelSubscription
from billing.get_billing_history import GetBillingHistory
from billing.stripe_subscription_manager import StripeSubscriptionManager
from customer.update_name import UpdateName
from customer.update_password import UpdatePassword
from doc.serve_documentation import ServeDocumentation
from event_type_enum import EventType

firebase_cred = os.environ['FIREBASE_CREDENTIALS']
print(f'FIREBASE CRED - {firebase_cred}')
# Initialize Firebase Admin SDK
cred = credentials.Certificate(json.loads(os.environ['FIREBASE_CREDENTIALS']))
firebase_admin.initialize_app(cred)


def lambda_handler(event, context):
    path = event.get('path')
    event_type = EventType.from_path(path)
    # Authentication
    if event_type == 'REGISTER':
        handler = Register(event)
        response = handler.create_user()
    elif event_type == 'LOGIN':
        handler = Login(event)
        response = handler.authenticate_user()
    elif event_type == 'SOCIAL_LOGIN':
        handler = SocialLogin(event)
        response = handler.verify_social_token()
    elif event_type == 'RESET_PASSWORD':
        handler = ResetPassword(event)
        response = handler.send_reset_email()
    elif event_type == 'GET_USER_PROFILE':
        handler = GetUserProfile(event)
        response = handler.fetch_user_profile()
    # Customer
    elif event_type == 'UPDATE_PASSWORD':
        handler = UpdatePassword(event)
        body = json.loads(event['body'])
        response = handler.update_password(body['current_password'], body['new_password'])
    elif event_type == 'UPDATE_NAME':
        handler = UpdateName(event)
        response = handler.update_user_name()
    elif event_type == 'GET_LOCALE':
        ip_address = event['requestContext']['identity']['sourceIp']
        response = get_location_info(ip_address)
    elif event_type == 'GET_USER_PROVIDER':
        query_params = event.get('queryStringParameters', {})
        handler = GetProvider()
        response = handler.check_provider(query_params.get('email', None), query_params.get('provider', None))
    # Billing
    elif event_type == 'CHECK_ALL_BILLING':
        handler = CheckBilling(event)
        response = handler.fetch_check_billing()
    elif event_type == 'CHECK_USER_BILLING':
        handler = CheckBilling(event)
        response = handler.fetch_check_billing_for_user()
    elif event_type == 'BUY_SUBSCRIPTION':
        handler = BuySubscription(event)
        response = handler.create_subscription()
    elif event_type == 'PROCESS_PAYPAL_SUBSCRIPTION':
        handler = ProcessPaypalSubscription(event)
        response = handler.process_paypal_subscription()
    elif event_type == 'GET_BILLING_HISTORY':
        handler = GetBillingHistory(event)
        response = handler.fetch_billing_history()
    elif event_type == 'CANCEL_SUBSCRIPTION':
        handler = CancelSubscription(event)
        response = handler.cancel_subscription()
    elif event_type == 'RENEW_SUBSCRIPTION':
        handler = BuySubscription(event)
        response = handler.renew_subscription()
    elif event_type == 'UPDATE_SUBSCRIPTION':
        handler = BuySubscription(event)
        response = handler.update_subscription()
    elif event_type == 'GET_ALL_SUBSCRIPTIONS':
        handler = StripeSubscriptionManager(event)
        response = handler.get_all_subscriptions()
    # Documentation
    elif event_type == 'DOC':
        handler = ServeDocumentation()
        response = handler.serve_documentation()
    elif event_type == 'OPENAPI':
        handler = ServeDocumentation()
        response = handler.serve_openapi()

    # contact us
    elif event_type == 'CONTACT_US':
        handler = ContactUs(event)
        response = handler.sendEmail()
    else:
        response = {
            'statusCode': 400,
            'body': json.dumps('Invalid event type')
        }

    return response
