import json
import traceback

from firebase_admin import auth

from billing.check_billing import CheckBilling
from db.db_manager import DbManager
from utils.build_response import build_response


class Register:
    def __init__(self, event):
        self.event = event
        self.body = json.loads(event['body'])
        self.email = self.body['email']
        self.password = self.body['password']
        # self.image_url = self.body['image_url']
        self.db_manager = DbManager()

    def create_user(self):
        try:
            # Create user in Firebase
            user = auth.create_user(
                email=self.email,
                password=self.password
            )

            # Store user details in the database without the password
            query = "INSERT INTO users (uid, email, provider_type) VALUES (%s, %s, 'email_credentials')"
            self.db_manager.execute_query(query, (user.uid, self.email))
            handler = CheckBilling(self.event)
            handler.fetch_check_billing_for_user_register(user.uid)
            self.db_manager.close()
        except Exception as e:
            traceback.print_exc()
            return build_response(400, {'error': str(e)})
        return build_response(200, 'User registered successfully!')

