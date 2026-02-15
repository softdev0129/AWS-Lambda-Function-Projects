from db.db_manager import DbManager
from decorators.verify_firebase_token import verify_firebase_token
from utils.build_response import build_response
import traceback


class CheckBilling:
    def __init__(self, event):
        self.event = event
        self.db_manager = DbManager()

    def fetch_check_billing_for_user_register(self, uid):
        self.create_billing_account_if_not_exist(uid)

    @verify_firebase_token
    def fetch_check_billing_for_user(self, uid):
        self.create_billing_account_if_not_exist(uid)

    def create_billing_account_if_not_exist(self, uid):
        try:
            # Fetch user details from the database
            query = "SELECT * FROM users WHERE uid = %s"
            user = self.db_manager.fetch_one(query, (uid,))

            if not user:
                return build_response(404, {'error': 'User not found'})

            print(f'Check billing_credit_id and billing_subscription_id for {user}')
            if user[5] is None:
                print(f'Creating billing_credit_id  for {user}')
                billing_credit_id = self.create_billing_credit(user)
                update_query = "UPDATE users SET billing_credit_id = %s WHERE id = %s"
                self.db_manager.execute_query(update_query, (billing_credit_id, user[0]))

            if user[5] is None:
                print(f'Creating billing_subscription_id  for {user}')
                billing_subscription_id = self.create_billing_subscription(user)
                update_query = "UPDATE users SET billing_subscription_id = %s WHERE id = %s"
                self.db_manager.execute_query(update_query, (billing_subscription_id, user[0]))

            print({'user_profile': user})
        except Exception as e:
            traceback.print_exc()
            print({'error': str(e)})

    def fetch_check_billing(self):
        try:
            # Fetch user details from the database
            query = "SELECT * FROM users WHERE billing_credit_id IS NULL OR billing_subscription_id IS NULL"
            users = self.db_manager.fetch_all(query)

            for user in users:
                if user[5] is None:
                    billing_credit_id = self.create_billing_credit(user)
                    update_query = "UPDATE users SET billing_credit_id = %s WHERE id = %s"
                    self.db_manager.execute_query(update_query, (billing_credit_id, user[0]))
                if user[5] is None:
                    billing_subscription_id = self.create_billing_subscription(user)
                    update_query = "UPDATE users SET billing_subscription_id = %s WHERE id = %s"
                    self.db_manager.execute_query(update_query, (billing_subscription_id, user[0]))

            if not users:
                print({'error': 'User not found'})

            user_profile = users[0]

            print({'user_profile': user_profile})
        except Exception as e:
            traceback.print_exc()
            return print({'error': str(e)})

    def create_billing_credit(self, user):
        try:
            # Define the billing credit details
            billing_credit_type = 'default'  # or fetch this from user if needed
            billing_credit_amount = 0  # or calculate based on some logic

            # Insert the billing credit into the database
            insert_query = """
                INSERT INTO billing_credit (type, amount) 
                VALUES (%s, %s) 
                RETURNING id
            """
            billing_credit_id = self.db_manager.fetch_one(insert_query, (billing_credit_type, billing_credit_amount))
            return billing_credit_id[0]
        except Exception as e:
            traceback.print_exc()
            print(f"Error creating billing credit: {str(e)}")

    def create_billing_subscription(self, user):
        try:
            # Define the subscription details
            user_id = user[0]
            subscription_id = None  # or generate/fetch this from another service or logicN
            # Insert the billing subscription into the database
            insert_query = """
                INSERT INTO billing_subscription (user_id, subscription_id) 
                VALUES (%s, %s) 
                RETURNING id
            """
            billing_subscription_id = self.db_manager.fetch_one(insert_query, (user_id, subscription_id))
            return billing_subscription_id[0]
        except Exception as e:
            traceback.print_exc()
            print(f"Error creating billing subscription: {str(e)}")
