import json
import os
import stripe
from firebase_admin import auth
from db.db_manager import DbManager
from utils.build_response import build_response
from decorators.verify_firebase_token import verify_firebase_token


class CancelSubscription:
    def __init__(self, event):
        self.event = event
        self.db_manager = DbManager()
        # Initialize Stripe API
        stripe.api_key = os.environ['STRIPE_API_KEY']

    @verify_firebase_token
    def cancel_subscription(self, uid):
        try:
            # Fetch user details from the database
            query = "SELECT id, stripe_customer_id, billing_credit_id FROM users WHERE uid = %s"
            user = self.db_manager.fetch_one(query, (uid,))

            if not user:
                return build_response(404, {'error': 'User not found'})

            stripe_customer_id = user[1]
            user_id = user[0]
            billing_credit_id = user[2]
            query = "SELECT stripe_subscription_id FROM billing_subscription WHERE user_id = %s"
            stripe_subscription_id_data = self.db_manager.fetch_one(query, (user_id,))
            stripe_subscription_id = stripe_subscription_id_data[0]
            # Fetch the subscription
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)

            stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=True
            )

            if subscription.customer != stripe_customer_id:
                return build_response(403, {'error': 'Unauthorized'})

            # Cancel the subscription
            stripe.Subscription.delete(stripe_subscription_id)
            query = "UPDATE billing_subscription SET subscription_id = NULL, stripe_subscription_id = NULL WHERE user_id = %s"
            self.db_manager.execute_query(query, (user_id,))
            query = "UPDATE billing_credit SET type = 'default', amount = 0 WHERE id = %s"
            self.db_manager.execute_query(query, (billing_credit_id,))
            self.db_manager.close()
            return build_response(200, 'Subscription canceled successfully!')
        except Exception as e:
            return build_response(400, {'error': str(e)})
