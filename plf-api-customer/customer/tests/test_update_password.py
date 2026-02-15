import unittest
import json
from unittest.mock import patch, MagicMock
from customer.update_password import UpdatePassword

class TestUpdatePassword(unittest.TestCase):
    @patch('customer.update_password.DbManager')
    @patch('customer.update_password.auth')
    def test_update_password(self, mock_auth, mock_db_manager):
        # Arrange
        event = {'headers': {'Authorization': 'Bearer test_token'}, 'body': '{"current_password": "old_password", "new_password": "new_password"}'}
        mock_auth.verify_id_token.return_value = {'uid': 'uid'}

        # Act
        update_password = UpdatePassword(event)
        response = update_password.update_password()

        # Assert
        mock_auth.verify_id_token.assert_called_once_with('test_token')
        mock_auth.update_user.assert_called_once_with('uid', password='new_password')
        
        expected_message = 'Password updated successfully'
        self.assertEqual(json.loads(response['body']['message']), expected_message)

        print("UpdatePassword UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()