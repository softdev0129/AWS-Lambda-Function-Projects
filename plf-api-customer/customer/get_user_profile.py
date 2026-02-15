import traceback
from firebase_admin import auth
from db.db_manager import DbManager
from decorators.verify_firebase_token import verify_firebase_token
from utils.build_response import build_response
import requests
from datetime import date, datetime


class GetUserProfile:
    def __init__(self, event):
        self.event = event
        self.db_manager = DbManager()

    @verify_firebase_token
    def fetch_user_profile(self, uid):
        try:
            # Fetch user details and billing info from the database
            query = """
            SELECT 
                u.uid,
                u.email,
                u.account_name,
                u.stripe_customer_id,
                u.provider_type,
                bc.type AS credit_type,
                bc.amount AS credit_amount,
                bs.subscription_id,
                bs.current_period_end,
                s.product_name,
                s.product_description,
                s.price_value,
                s.currency_code,
                s.tier
            FROM users u
            LEFT JOIN billing_credit bc ON u.billing_credit_id = bc.id
            LEFT JOIN billing_subscription bs ON u.billing_subscription_id = bs.id
            LEFT JOIN subscription s ON bs.subscription_id = s.subscription_id
            WHERE u.uid = %s
            """
            print(f'user!!!')
            user = self.db_manager.fetch_one(query, (uid,))

            print(f'user!!!{user}')
            self.db_manager.close()

            if not user:
                return build_response(404, {'error': 'User not found'})

            # Extracting data from the database query
            uid, email, account_name, stripe_customer_id, provider_type, credit_type, credit_amount, subscription_id, current_period_end, product_name, product_description, price_value, currency_code, tier = user

            apikey = '81ee0ad474b99468f94d13160fee23add9999c7ee0a58baafb749841d9039569f20ed77ddcf9acac74d4d4bdaa58213f92019e941df6ec00eea7fabde38c2912a9aa00b729587a7276eb5df05f0bd118f581df70b07be703c500aa6050af2d76c17c7f7c176023bb8ae7bd5f4792f56d97d6115189d09b2c159b3b8ca96f0c10'
            headers = {
                "Authorization": f"Bearer {apikey}"
            }
            url = 'https://dev-env.primeleadfinder.com/api/plf-subscription?populate=PlfSubscription.features&populate=PlfSubscription.benefits&populate=PlfSubscription.tags'
            response = requests.get(url, headers=headers)
            response_data = response.json()
            details = None
            if subscription_id is not None and 'error' not in response_data:
                for data in response_data['data']['attributes']['PlfSubscription']:
                    if data['name'] in product_name:
                        details = data

            formatted_datetime = None
            if isinstance(current_period_end, (datetime, date)):
                formatted_datetime = current_period_end.isoformat()
            # Constructing categorized response data
            user_profile = {
                'user_details': {
                    'uid': uid,
                    'email': email,
                    'account_name': account_name,
                    'stripe_customer_id': stripe_customer_id,
                    'provider_type': provider_type
                },
                'billing_info': {
                    'credit_type': credit_type,
                    'credit_amount': credit_amount,
                    'renew_or_expires_at': formatted_datetime
                },
                'subscription_info': None if subscription_id is None else {
                    'subscription_id': subscription_id,
                    'product_name': product_name,
                    'product_description': product_description,
                    'price_value': price_value,
                    'currency_code': currency_code,
                    'details': details,
                    'tier': tier
                }
            }

            return build_response(200, user_profile)

        except Exception as e:
            traceback.print_exc()
            return build_response(400, {'error': str(e)})
