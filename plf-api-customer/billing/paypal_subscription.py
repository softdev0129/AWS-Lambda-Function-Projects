import json
import os
from datetime import datetime
import requests

from db.db_manager import DbManager
from utils.build_response import build_response, build_error_response
from decorators.verify_firebase_token import verify_firebase_token


class ProcessPaypalSubscription:
    def __init__(self, event):
        self.event = event
        self.body = json.loads(event['body'])
        self.paypal_subscription_id = self.body.get('paypal_subscription_id')
        self.subscription_id = self.body.get('subscription_id')
        self.db_manager = DbManager()

    @verify_firebase_token
    def process_paypal_subscription(self, uid):
        try:
            user = self._get_user(uid)
            if not user:
                return build_response(404, {'error': 'User not found'})

            # Fetch PayPal subscription details
            subscription_info = self._get_paypal_subscription_info(self.paypal_subscription_id)
            if not subscription_info:
                return build_error_response(400, {'error': 'Subscription not found'})

            # Extract details from PayPal subscription
            subscription_id = subscription_info['id']
            current_period_end = datetime.fromtimestamp(
                int(subscription_info['billing_info']['next_billing_date']) / 1000)

            # Update local subscription in the database
            self._update_local_subscription(uid, self.subscription_id, subscription_id, current_period_end)

            return build_response(200, {'subscription_id': subscription_id})

        except Exception as e:
            return build_error_response(400, {'error': str(e)})

        finally:
            self.db_manager.close()

    def _get_paypal_subscription_info(self, subscription_id):
        """
        Fetch subscription details from PayPal API.
        """
        paypal_api_url = f'https://api.paypal.com/v1/billing/subscriptions/{subscription_id}'
        headers = {
            'Authorization': f'Bearer {self._get_paypal_access_token()}',
            'Content-Type': 'application/json'
        }
        response = requests.get(paypal_api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _get_paypal_access_token(self):
        """
        Get an access token from PayPal API.
        """
        client_id = os.getenv('PAYPAL_CLIENT_ID')
        client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        auth_url = 'https://api.paypal.com/v1/oauth2/token'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {'grant_type': 'client_credentials'}
        response = requests.post(auth_url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception('Failed to obtain PayPal access token')

    def _update_local_subscription(self, uid, local_subscription_id, subscription_id, current_period_end):
        """
        Update the local subscription in the database.
        """
        update_query = """
            UPDATE billing_subscription
            SET paypal_subscription_id = %s, subscription_id = %s, current_period_end = %s, updated_at = %s
            WHERE user_id = %s
        """
        self.db_manager.execute(
            update_query,
            (local_subscription_id, subscription_id, current_period_end, datetime.utcnow(), uid)
        )

    def _get_user(self, uid):
        """
        Get user from the database.
        """
        return self.db_manager.get_user(uid)
