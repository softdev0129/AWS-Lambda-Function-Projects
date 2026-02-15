import unittest
import json
from unittest.mock import patch, MagicMock
from auth.social_login import SocialLogin

class TestSocialLogin(unittest.TestCase):
    @patch('auth.social_login.auth.verify_id_token')
    @patch('auth.social_login.auth.create_custom_token')
    @patch('auth.social_login.DbManager')
    def test_verify_social_token(self, mock_db_manager, mock_create_custom_token, mock_verify_id_token):
        # Arrange
        event = {'body': '{"provider": "test_provider", "id_token": "test_token"}'}
        mock_db_manager.return_value.fetch_one.return_value = None
        mock_verify_id_token.return_value = {'uid': 'uid', 'email': 'email', 'name': 'name'}
        mock_create_custom_token.return_value = b'custom_token'

        # Act
        social_login = SocialLogin(event)
        response = social_login.verify_social_token()

        # Assert
        mock_verify_id_token.assert_called_once_with('test_token')
        mock_db_manager.return_value.fetch_one.assert_called_once_with("SELECT * FROM users WHERE uid = %s", ('uid',))
        mock_db_manager.return_value.execute_query.assert_called_once_with("INSERT INTO users (uid, email, username) VALUES (%s, %s, %s)", ('uid', 'email', 'name'))
        mock_create_custom_token.assert_called_once_with('uid')
        expected_message = {'token': 'custom_token'}
        self.assertEqual(response['body']['message'], json.dumps(expected_message))

        print("Social Login UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()