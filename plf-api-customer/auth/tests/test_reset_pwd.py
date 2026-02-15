import unittest
import json
from unittest.mock import patch, MagicMock
from auth.reset_password import ResetPassword

class TestResetPassword(unittest.TestCase):
    @patch('boto3.client')
    @patch.dict('os.environ', {'FROM_EMAIL': 'mock_value', 'AWS_ACCESS_KEY_ID': 'mock_value', 'AWS_SECRET_ACCESS_KEY': 'mock_value'}, clear=True)
    @patch('auth.reset_password.auth.generate_password_reset_link')
    def test_send_reset_email(self, mock_reset_link, mock_boto3_client):
        # Arrange
        event = {'body': '{"email": "test@test.com"}'}
        mock_ses_client = MagicMock()
        mock_boto3_client.return_value = mock_ses_client
        mock_reset_link.return_value = 'https://reset_link'

        # Act
        reset_password = ResetPassword(event)
        response = reset_password.send_reset_email()

        # Assert
        mock_reset_link.assert_called_once_with('test@test.com')
        mock_boto3_client.assert_called_once_with('ses', region_name='eu-west-1', aws_access_key_id='mock_value', aws_secret_access_key='mock_value')
        mock_ses_client.send_email.assert_called_once()

        expected_message = {'message': 'Password reset email sent successfully!'}
        self.assertEqual(response['body']['message'], json.dumps(expected_message))

        print("Reset Password UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()