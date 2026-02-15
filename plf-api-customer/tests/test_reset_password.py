import unittest
from unittest.mock import patch, MagicMock
import json

from auth.reset_password import ResetPassword


class TestResetPassword(unittest.TestCase):

    @patch('firebase_admin.auth.generate_password_reset_link')
    @patch('boto3.client')
    def test_send_reset_email_success(self, mock_boto3_client, mock_generate_password_reset_link):
        # Mocking the generate_password_reset_link function
        mock_generate_password_reset_link.return_value = "https://example.com/reset-link"

        # Mocking the send_email function of boto3 SES client
        mock_ses_client_instance = MagicMock()
        mock_ses_client_instance.send_email.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        mock_boto3_client.return_value = mock_ses_client_instance

        # Mock event data (simulating API Gateway event)
        event = {
            'body': json.dumps({'email': 'test@example.com'})
        }

        # Create an instance of ResetPassword
        reset_password_instance = ResetPassword(event)

        # Call send_reset_email method
        response = reset_password_instance.send_reset_email()

        # Assert the response
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Password reset email sent successfully!', json.loads(response['body'])['message'])

        # Assert that generate_password_reset_link was called with the correct email
        mock_generate_password_reset_link.assert_called_once_with('test@example.com')

        # Assert that send_email was called with the correct parameters
        mock_ses_client_instance.send_email.assert_called_once_with(
            Source=reset_password_instance.from_email,
            Destination={'ToAddresses': ['test@example.com']},
            Message={
                'Subject': {'Data': 'Password Reset Request', 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': 'Please click the following link to reset your password: <a href="https://example.com/reset-link">https://example.com/reset-link</a>', 'Charset': 'UTF-8'}}
            }
        )

    @patch('firebase_admin.auth.generate_password_reset_link')
    @patch('boto3.client')
    def test_send_reset_email_failure(self, mock_boto3_client, mock_generate_password_reset_link):
        # Mocking the generate_password_reset_link function
        mock_generate_password_reset_link.return_value = "https://example.com/reset-link"

        # Mocking the send_email function of boto3 SES client to raise an exception
        mock_ses_client_instance = MagicMock()
        mock_ses_client_instance.send_email.side_effect = Exception('InvalidEmailException')
        mock_boto3_client.return_value = mock_ses_client_instance

        # Mock event data (simulating API Gateway event)
        event = {
            'body': json.dumps({'email': 'test@example.com'})
        }

        # Create an instance of ResetPassword
        reset_password_instance = ResetPassword(event)

        # Call send_reset_email method
        response = reset_password_instance.send_reset_email()

        # Assert the response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('InvalidEmailException', json.loads(response['body'])['error'])

        # Assert that generate_password_reset_link was called with the correct email
        mock_generate_password_reset_link.assert_called_once_with('test@example.com')

        # Assert that send_email was called with the correct parameters
        mock_ses_client_instance.send_email.assert_called_once_with(
            Source=reset_password_instance.from_email,
            Destination={'ToAddresses': ['test@example.com']},
            Message={
                'Subject': {'Data': 'Password Reset Request', 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': 'Please click the following link to reset your password: <a href="https://example.com/reset-link">https://example.com/reset-link</a>', 'Charset': 'UTF-8'}}
            }
        )

if __name__ == '__main__':
    unittest.main()

