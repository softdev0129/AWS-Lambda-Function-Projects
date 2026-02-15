import json
import os
import requests
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from db.db_manager import DbManager
from utils.build_response import build_response
from utils.extract_token import extract_token


class UpdatePassword:
    def __init__(self, event):
        self.event = event
        self.db_manager = DbManager()

    def update_password(self, current_password, new_password):  # Add uid as a parameter
        try:
            id_token = extract_token(self.event)
            decoded_token = auth.verify_id_token(id_token)

            # Extract user ID from the decoded token
            uid = decoded_token['uid']
            email = decoded_token['email']
            # Verify the current password
            api_key = os.getenv('FIREBASE_API_KEY')
            url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
            payload = {
                'email': email,
                'password': current_password,
                'returnSecureToken': True
            }
            response = requests.post(url, data=json.dumps(payload))
            response_data = response.json()

            if 'error' in response_data:
                return build_response(401, {'message': response_data['error']['message']})

            # Update the password
            auth.update_user(uid, password=new_password)

            return build_response(200, 'Password updated successfully')

        except FirebaseError as e:
            return build_response(401, {'error': str(e)})
