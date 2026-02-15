from db.db_manager import DbManager
from utils.build_response import build_response


class GetProvider:
    def __init__(self):
        self.db_manager = DbManager()

    def check_provider(self, email, provider):
        try:
            query = "SELECT email, provider_type FROM users WHERE email = %s"
            user = self.db_manager.fetch_one(query, (email,))
            self.db_manager.close()
            if user is None:
                return build_response(404, {'message': 'User not found'})
            if user[1] == provider:
                return build_response(202, {})
            else:
                return build_response(400, {'message': f'User not using provider {provider}'})
        except Exception as e:
            return build_response(401, str(e))

