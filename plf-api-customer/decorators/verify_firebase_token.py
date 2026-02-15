from functools import wraps
from firebase_admin import auth
from firebase_admin.auth import ExpiredIdTokenError
from utils.build_response import build_response, build_error_response
from utils.extract_token import extract_token


def verify_firebase_token(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            id_token = extract_token(self.event)
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)

            # Extract user ID from the decoded token
            uid = decoded_token['uid']

            # Call the wrapped function with the user ID and other arguments
            return func(self, uid, *args, **kwargs)

        except ValueError as e:
            return build_error_response(401, str(e))

        except ExpiredIdTokenError:
            # Handle expired token error
            return build_error_response(401, 'Token has expired')

        except IndexError:
            return build_error_response(400, 'Invalid Authorization header format')
        except Exception as e:
            return build_error_response(400, str(e))

    return wrapper
