import json
import os
import stripe
import sys, traceback
from firebase_admin import auth
from db.db_manager import DbManager
from utils.build_response import build_response, build_error_response
from decorators.verify_firebase_token import verify_firebase_token


class GetBillingHistory:
    def __init__(self, event):
        self.event = event
        self.db_manager = DbManager()
        stripe.api_key = os.environ['STRIPE_API_KEY']

    @verify_firebase_token
    def fetch_billing_history(self, uid):
        try:
            # Fetch user details from the database
            query = "SELECT stripe_customer_id FROM users WHERE uid = %s"
            user = self.db_manager.fetch_one(query, (uid,))
            self.db_manager.close()

            if not user or not user[0]:
                return build_error_response(404, 'Stripe customer ID not found for user')

            stripe_customer_id = user[0]

            # Fetch invoices for the customer
            invoices = stripe.Invoice.list(customer=stripe_customer_id)

            # Format the response
            billing_history = []
            for invoice in invoices.auto_paging_iter():
                billing_history.append({
                    'id': invoice.id,
                    'amount_due': invoice.amount_due,
                    'amount_paid': invoice.amount_paid,
                    'amount_remaining': invoice.amount_remaining,
                    'currency': invoice.currency,
                    'description': invoice.lines.data[0].description,
                    'status': invoice.status,
                    'period_start': invoice.period_start,
                    'period_end': invoice.period_end,
                    'due_date': invoice.due_date,
                    'paid': invoice.paid
                })

            return build_response(200, {'billing_history': billing_history})

        except stripe.error.StripeError as e:
            traceback.print_exc(file=sys.stdout)
            # Handle Stripe specific errors
            return build_response(200, {'billing_history': []})

        except Exception as e:
            # Handle other exceptions
            traceback.print_exc()
            return build_error_response(400, str(e))
