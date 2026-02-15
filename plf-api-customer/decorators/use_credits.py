from functools import wraps
from firebase_admin import auth
from utils.build_response import build_response

def use_credits(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            auth_header = self.event['headers'].get('Authorization', '')

            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
            else:
                id_token = auth_header

            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            return func(self, uid, *args, **kwargs)
        except ValueError as e:
            return build_response(401, {'error': str(e)})
        except IndexError:
            return build_response(400, {'error': 'Invalid Authorization header format'})

    def __fetch_available_credits(self, uid):
        query = "SELECT credits FROM users WHERE uid = %s"
        result = self.db_manager.fetch_one(query, (uid,))
        if result:
            return result[0]
        return 0

    def __buy_search_directory_view_with_credits(self, uid):
        available_credits = self.__fetch_available_credits(uid)
        if available_credits > 0:
            # Deduct one credit for buying the view
            update_query = "UPDATE users SET credits = credits - 1 WHERE uid = %s"
            self.db_manager.execute_query(update_query, (uid,))
            return build_response(200, {'message': 'Search directory view purchased'})
        else:
            return build_response(402, {'error': 'Insufficient credits'})

    wrapper.__fetch_available_credits = __fetch_available_credits
    wrapper.__buy_search_directory_view_with_credits = __buy_search_directory_view_with_credits

    return wrapper
