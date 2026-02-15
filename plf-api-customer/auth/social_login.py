import json
import traceback

import jwt
import os
import requests
from firebase_admin import auth
from db.db_manager import DbManager
from utils.build_response import build_response
from billing.check_billing import CheckBilling
from utils.extract_token import extract_token


class SocialLogin:
    def __init__(self, event):
        self.event = event
        self.body = json.loads(event['body'])
        self.sign_in_provider = self.body['sign_in_provider']
        self.db_manager = DbManager()

    def verify_social_token(self):
        try:
            id_token = extract_token(self.event)
            if self.sign_in_provider == 'linkedin':
                linkedin_info = jwt.decode(id_token, options={"verify_signature": False})
                uid = linkedin_info['uid']
                additional_claims = linkedin_info['claims']
                sign_in_provider = additional_claims['sign_in_provider']
                if sign_in_provider != 'linkedin':
                    return build_response(401, {"Error:", "It can't sign in to our website with this sign-in provider"})
                custom_token = auth.create_custom_token(uid, additional_claims)

                api_key = os.getenv('FIREBASE_API_KEY')
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
                # Payload for the request
                payload = {
                    'token': custom_token.decode('utf-8'),
                    'returnSecureToken': True
                }

                # Send the request
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    id_token = response.json().get('idToken')
                else:
                    return build_response(401, {"Error:", response.json()})

            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name')
            photo = decoded_token.get('picture')
            provider = decoded_token.get('firebase', {}).get('sign_in_provider')
            if provider == "custom":
                provider = decoded_token.get('sign_in_provider')
        except Exception as e:
            traceback.print_exc()
            return build_response(401, str(e))

        query = "SELECT * FROM users WHERE email = %s"
        result = self.db_manager.fetch_one(query, (email,))

        if not result:
            query = "INSERT INTO users (uid, email, account_name, image_url, provider_type) VALUES (%s, %s, %s, %s, %s)"
            self.db_manager.execute_query(query, (uid, email, name, photo, provider))
            handler = CheckBilling(self.event)
            handler.fetch_check_billing_for_user_register(uid)
        else:
            if provider != result[8]:
                self.db_manager.close()
                return build_response(400, {'error': "You didn't sign up to our website with current provider."})
            query = "UPDATE users SET last_logged_in = CURRENT_TIMESTAMP WHERE email = %s"
            self.db_manager.execute_query(query, (email,))

        self.db_manager.close()
        return build_response(202, {'id_token': id_token})
