import json
from db.db_manager import DbManager
from decorators.verify_firebase_token import verify_firebase_token
from utils.build_response import build_response


class UpdateName:
    def __init__(self, event):
        self.event = event
        self.body = json.loads(event['body'])
        self.new_name = self.body['account_name']
        self.db_manager = DbManager()

    @verify_firebase_token
    def update_user_name(self, uid):
        if self.new_name is None:
            return build_response(400, 'Name is required')

        try:
            self.db_manager.update_user_name(uid, self.new_name)
            self.db_manager.close()
            return build_response(200, 'Name is updated successfully')

        except Exception as e:
            return build_response(500, {'error': str(e)})
