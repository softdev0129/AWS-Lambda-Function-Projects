import json
from firebase_admin import auth
from db.db_manager import DbManager
from utils.build_response import build_response


class CreateBilling:
    def __init__(self, event):
        self.body = json.loads(event['body'])
        self.email = self.body['email']
        self.password = self.body['password']
        self.token = event['headers'].get('Authorization')
        self.db_manager = DbManager()

    def create_billing_credit(self):
        try:
            # Create user in Firebase
            amount = 100
            billing_type = "standard"

            # Store user details in the database without the password
            query = "INSERT INTO billing_credit (type, amount) VALUES (%s, %s)"
            self.db_manager.execute_query(query, (billing_type, amount))
            self.db_manager.close()

            return build_response(200, 'Billing created successfully!')

        except Exception as e:
            return build_response(400, {'error': str(e)})
    