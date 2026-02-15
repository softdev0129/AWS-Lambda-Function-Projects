import stripe
import os
import traceback
import requests
from db.db_manager import DbManager
from decorators.verify_firebase_token import verify_firebase_token
from utils.build_response import build_response


def _fetch_prices_by_product_id(product_id):
    """Fetch prices from Stripe for a specific product_id."""
    prices = []
    try:
        # Fetch prices for the specified product_id, handling pagination
        stripe_prices = stripe.Price.list(product=product_id, limit=100)  # Adjust limit as necessary
        prices.extend(stripe_prices.data)

        while stripe_prices.has_more:
            stripe_prices = stripe.Price.list(
                product=product_id,
                limit=100,
                starting_after=stripe_prices.data[-1].id
            )
            prices.extend(stripe_prices.data)

        return [
            {
                'price_id': price.id,
                'product_id': price.product,
                'price_value': price.unit_amount,
                'currency_code': price.currency,
                'billing_scheme': price.billing_scheme,
                'interval': price.recurring.interval if price.recurring else None,
                'interval_count': price.recurring.interval_count if price.recurring else None
            }
            for price in prices
        ]
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe API error: {str(e)}")


class StripeSubscriptionManager:
    def __init__(self, event):
        self.event = event
        # Initialize Stripe API with your API key
        stripe.api_key = os.environ.get('STRIPE_API_KEY')

        # Initialize PostgreSQL database connection
        self.db_manager = DbManager()

        # Predefined list of subscriptions
        self.subscriptions = [
            {
                'product_name': 'Premium Subscription',
                'product_description': 'Premium subscription service',
                'price_value': 1999,  # in cents (e.g., $19.99)
                'currency_code': 'USD'
            },
            {
                'product_name': 'Basic Subscription',
                'product_description': 'Basic subscription service',
                'price_value': 999,  # in cents (e.g., $9.99)
                'currency_code': 'USD'
            }
            # Add more subscriptions as needed
        ]

    def get_all_subscriptions(self):
        try:
            apikey = '81ee0ad474b99468f94d13160fee23add9999c7ee0a58baafb749841d9039569f20ed77ddcf9acac74d4d4bdaa58213f92019e941df6ec00eea7fabde38c2912a9aa00b729587a7276eb5df05f0bd118f581df70b07be703c500aa6050af2d76c17c7f7c176023bb8ae7bd5f4792f56d97d6115189d09b2c159b3b8ca96f0c10'
            headers = {
                "Authorization": f"Bearer {apikey}"
            }
            url = 'https://dev-env.primeleadfinder.com/api/plf-subscription?populate=PlfSubscription.features&populate=PlfSubscription.benefits&populate=PlfSubscription.tags'
            response = requests.get(url, headers=headers)
            response_data = response.json()
            if 'error' in response_data:
                return build_response(401, response_data['error']['message'])

            select_query = "SELECT * FROM subscription"
            subscriptions_data = self.db_manager.fetch_all(select_query)
            self.db_manager.close()

            if subscriptions_data is None:
                subscriptions_data = []
            for data in response_data['data']['attributes']['PlfSubscription']:
                data['product_info'] = {
                    'subscription_id': None,
                    'product_name': None,
                    'product_description': None,
                    'product_id': None,
                    'price_id': None,
                    'price_value': None,
                    'currency_code': None,
                    'credit_value': None,
                    'months_off_annual_discount': None
                }
                for subscription_data in subscriptions_data:
                    if data['name'] in subscription_data[1]:
                        data['product_info']['subscription_id'] = subscription_data[0]
                        data['product_info']['product_name'] = subscription_data[1]
                        data['product_info']['product_description'] = subscription_data[2]
                        data['product_info']['product_id'] = subscription_data[3]
                        data['product_info']['price_id'] = subscription_data[4]
                        data['product_info']['price_value'] = subscription_data[5]
                        data['product_info']['currency_code'] = subscription_data[6]
                        data['product_info']['credit_value'] = subscription_data[7]
                        data['product_info']['months_off_annual_discount'] = subscription_data[8]
                        data['product_info']['paypal_product_id'] = subscription_data[9]
                        data['product_info']['stripe_product_id'] = subscription_data[10]
                        data['product_info']['tier'] = subscription_data[11]
                        data['product_info']['prices'] = _fetch_prices_by_product_id(subscription_data[3])
                        break
        except Exception as error:
            return build_response(400, {'error': str(error)})
        return build_response(200, response_data['data']['attributes'])

    def close_connection(self):
        self.db_manager.close()
