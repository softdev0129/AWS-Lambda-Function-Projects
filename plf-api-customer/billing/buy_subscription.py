import json
import os
from decimal import Decimal

import stripe
from db.db_manager import DbManager
from utils.build_response import build_response, build_error_response
from decorators.verify_firebase_token import verify_firebase_token
from datetime import datetime


class BuySubscription:
    def __init__(self, event):
        self.event = event
        self.body = json.loads(event['body'])
        self.payment_method_id = self.body.get('payment_method_id')
        self.subscription_id = self.body.get('subscription_id')
        self.new_subscription_id = self.body.get('new_subscription_id')
        self.interval = self.body.get('interval', 'month')
        self.db_manager = DbManager()

        # Initialize Stripe API
        stripe.api_key = os.environ['STRIPE_API_KEY']

    @verify_firebase_token
    def create_subscription(self, uid):
        try:
            user = self._get_user(uid)
            if not user:
                return build_response(404, {'error': 'User not found'})

            stripe_customer_id = self._get_or_create_stripe_customer(user)
            subscription_info = self._get_subscription_info(self.subscription_id)

            # Fetch product_id from subscription_info and get prices
            product_id = subscription_info['product_id']
            prices = self._fetch_prices_by_product_id(product_id)
            matching_price = next((price for price in prices if price.get('interval') == self.interval), None)
            if not matching_price:
                return build_error_response(400, {'error': 'No matching price found for the specified interval'})

            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{'price': matching_price['price_id']}],
                description=subscription_info['description'],
                payment_settings={
                    "payment_method_types": ["card"]
                },
                expand=['latest_invoice.payment_intent'],
            )

            self._update_local_subscription(user['user_id'], subscription)
            self._update_billing_credit(subscription_info, user['billing_credit_id'])
            self._store_subscription_period_end(subscription.id, subscription.current_period_end)

            return build_response(200, {
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            })

        except stripe.error.StripeError as e:
            return build_response(400, {'error': str(e)})

        except Exception as e:
            return build_error_response(400, {'error': str(e)})

        finally:
            self.db_manager.close()

    @verify_firebase_token
    def update_subscription(self, uid):
        try:
            user = self._get_user(uid)
            if not user:
                return build_error_response(404, {'error': 'User not found'})

            stripe_customer_id = user['stripe_customer_id']
            subscription = self._get_active_subscription(stripe_customer_id)

            if not subscription:
                return build_error_response(404, {'error': 'No active subscription found'})

            # Retrieve new subscription info and fetch product_id
            new_subscription_info = self._get_subscription_info(self.new_subscription_id)
            product_id = new_subscription_info['product_id']
            prices = self._fetch_prices_by_product_id(product_id)
            matching_price = next((price for price in prices if price['interval'] == self.interval), None)
            if not matching_price:
                return build_error_response(400, {'error': f'No matching price found for the specified interval {subscription.id}'})

            print(subscription['items'])
            # Correct way to access subscription items
            if hasattr(subscription['items'], 'data'):
                item_id = subscription['items'].data[0].id
            else:
                return build_response(400, {'error': f'Subscription items are not available {subscription.id}'})

            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                items=[{
                    'id': item_id,
                    'price': matching_price['price_id']
                }],
                proration_behavior='create_prorations'
            )

            self._update_local_subscription(user['user_id'], updated_subscription)
            self._store_subscription_period_end(subscription.id, updated_subscription.current_period_end)

            return build_response(200, {
                'subscription_id': updated_subscription.id
            })

        except stripe.error.StripeError as e:
            return build_error_response(400, {'error': str(e)})

        except Exception as e:
            return build_error_response(400, {'error': str(e)})

        finally:
            self.db_manager.close()

    @verify_firebase_token
    def renew_subscription(self, uid):
        try:
            user = self._get_user(uid)
            if not user:
                return build_error_response(404, {'error': 'User not found'})

            stripe_customer_id = user['stripe_customer_id']
            subscription = self._get_active_subscription(stripe_customer_id)

            if not subscription:
                return build_error_response(404, {'error': 'No active subscription found'})

            renewed_subscription = stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=False
            )

            self._update_local_subscription(user['user_id'], renewed_subscription)
            self._store_subscription_period_end(subscription.id, renewed_subscription.current_period_end)

            return build_response(200, {
                'subscription_id': renewed_subscription.id
            })

        except stripe.error.StripeError as e:
            return build_error_response(400, {'error': str(e)})

        except Exception as e:
            return build_error_response(400, {'error': str(e)})

        finally:
            self.db_manager.close()

    def _get_user(self, uid):
        query = "SELECT id as user_id, email, stripe_customer_id, billing_credit_id FROM users WHERE uid = %s"
        result = self.db_manager.fetch_one(query, (uid,))
        return {
            'user_id': result[0],
            'email': result[1],  # Assuming product_id is at index 5
            'stripe_customer_id': result[2],  # Assuming product_id is at index 5
            'billing_credit_id': result[3],  # Assuming product_id is at index 5
        }

    def _get_or_create_stripe_customer(self, user):
        stripe_customer_id = user['stripe_customer_id']
        email = user['email']
        uid = user['user_id']
        if stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(stripe_customer_id)
                if customer.email != email:
                    customer.email = email
                    customer.save()
            except stripe.error.InvalidRequestError:
                return None
        else:
            customer = stripe.Customer.create(
                email=email,
                payment_method=self.payment_method_id,
                invoice_settings={'default_payment_method': self.payment_method_id}
            )
            stripe_customer_id = customer.id
            update_query = "UPDATE users SET stripe_customer_id = %s WHERE uid = %s"
            self.db_manager.execute_query(update_query, (stripe_customer_id, uid))
        return stripe_customer_id

    def _get_subscription_info(self, subscription_id):
        query = "SELECT * FROM subscription WHERE subscription_id = %s"
        subscription_info = self.db_manager.fetch_one(query, (subscription_id,))
        return {
            'description': subscription_info[2],
            'product_id': subscription_info[3],  # Assuming product_id is at index 5
            'credit_value': subscription_info[7]
        }

    def _update_local_subscription(self, user_id, subscription):
        current_period_end_dt = None
        if isinstance(subscription.current_period_end, (int, float, Decimal)):
            current_period_end_dt = datetime.fromtimestamp(float(subscription.current_period_end))

        update_query = """
            UPDATE billing_subscription
            SET subscription_id = %s, stripe_subscription_id = %s, current_period_end = %s, updated_at = %s
            WHERE user_id = %s
        """
        self.db_manager.execute_query(
            update_query,
            (self.subscription_id, subscription.id, current_period_end_dt, datetime.now(), user_id)
        )

    def _update_billing_credit(self, subscription_info, billing_credit_id):
        update_query = "UPDATE billing_credit SET type = %s, amount = %s WHERE id = %s"
        self.db_manager.execute_query(update_query, (self.interval, subscription_info['credit_value'], billing_credit_id))

    def _update_local_subscription_status(self, user_id):
        update_query = "UPDATE billing_subscription SET stripe_subscription_id = NULL, updated_at = %s WHERE user_id = %s"
        self.db_manager.execute_query(update_query, (datetime.now(), user_id))

    def _store_subscription_period_end(self, subscription_id, period_end):
        current_period_end_dt = None
        if isinstance(period_end, (int, float, Decimal)):
            current_period_end_dt = datetime.fromtimestamp(float(period_end))
        update_query = "UPDATE billing_subscription SET current_period_end = %s WHERE stripe_subscription_id = %s"
        self.db_manager.execute_query(update_query, (current_period_end_dt, subscription_id))

    def _get_active_subscription(self, stripe_customer_id):
        subscriptions = stripe.Subscription.list(customer=stripe_customer_id, status='active')
        if subscriptions.data:
            return subscriptions.data[0]
        return None

    def _fetch_prices_by_product_id(self, product_id):
        """Fetch prices from Stripe for a specific product_id."""
        prices = []
        try:
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
            return build_error_response(500, {'error': f"Stripe API error: {str(e)}"})
