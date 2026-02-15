import unittest
import json
from unittest.mock import patch, MagicMock
from auth.login import Login

class TestLogin(unittest.TestCase):
    @patch('requests.post')
    @patch('os.getenv')
    def test_authenticate_user(self, mock_getenv, mock_post):
        # Arrange
        event = {'body': '{"email": "test@test.com", "password": "password"}'}
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'idToken': 'fake_token'
        }
        mock_post.return_value = mock_response
        mock_getenv.return_value = 'fake_api_key'
        
        # Act
        login = Login(event)
        response = login.authenticate_user()
        
        # Assert
        mock_getenv.assert_called_once_with('FIREBASE_API_KEY')
        mock_post.assert_called_once_with('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=fake_api_key', 
                                          data=json.dumps({
                                              'email': 'test@test.com', 
                                              'password': 'password', 
                                              'returnSecureToken': True
                                          }))
        self.assertEqual(response, {
            'statusCode': 200,
            'body': {
                'message': json.dumps({'id_token': 'fake_token'})
            }
        })
        print("login UnitTest Successful!!!")


if __name__ == '__main__':
    unittest.main()