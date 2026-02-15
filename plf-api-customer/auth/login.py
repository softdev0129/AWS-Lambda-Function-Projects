import json
import os
import requests
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from utils.build_response import build_response
from db.db_manager import DbManager


class Login:
    def __init__(self, event):
        self.db_manager = DbManager()
        self.body = json.loads(event['body'])
        self.email = self.body['email']
        self.password = self.body['password']

    def authenticate_user(self):
        try:
            # Use Firebase's Identity Toolkit REST API to verify the email and password
            api_key = os.getenv('FIREBASE_API_KEY')
            url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
            payload = {
                'email': self.email,
                'password': self.password,
                'returnSecureToken': True
            }
            response = requests.post(url, data=json.dumps(payload))
            response_data = response.json()

            if 'error' in response_data:
                return build_response(401, response_data['error']['message'])

            query = "UPDATE users SET last_logged_in = CURRENT_TIMESTAMP WHERE email = %s"
            self.db_manager.execute_query(query, (self.email,))
            self.db_manager.close()

            id_token = response_data['idToken']
            return build_response(200, {'id_token': id_token})
        except FirebaseError as e:
            return build_response(401, {'error': str(e)})
