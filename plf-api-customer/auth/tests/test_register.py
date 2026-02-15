import unittest
import json
from unittest.mock import patch, MagicMock
from auth.register import Register

class TestRegister(unittest.TestCase):
    @patch('auth.register.auth')
    @patch('auth.register.DbManager')
    def test_create_user(self, mock_db_manager, mock_auth):
        # Arrange
        event = {'body': '{"email": "test@test.com", "password": "password"}'}
        user_mock = MagicMock()
        user_mock.uid = 'uid'
        mock_auth.create_user.return_value = user_mock
        mock_db_manager.return_value.execute_query.return_value = None

        # Act
        register = Register(event)
        response = register.create_user()

        # Assert
        mock_auth.create_user.assert_called_once_with(email='test@test.com', password='password')
        mock_db_manager.return_value.execute_query.assert_called_once_with("INSERT INTO users (uid, email) VALUES (%s, %s)", ('uid', 'test@test.com'))
        self.assertEqual(response, {
            'statusCode': 200,
            'body': {
                'message': json.dumps('User registered successfully!')
            }
        })
        print("Register UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()