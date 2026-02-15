import unittest
import json
from unittest.mock import patch, MagicMock
from billing.cancel_subscription import CancelSubscription

class TestCancelSubscription(unittest.TestCase):
    @patch('stripe.Subscription.delete')
    @patch('stripe.Subscription.retrieve')
    @patch('firebase_admin.auth.verify_id_token')
    @patch('billing.cancel_subscription.DbManager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'mock_value'}, clear=True)
    def test_cancel_subscription(self, mock_db_manager, mock_verify_id_token, mock_subscription_retrieve, mock_subscription_delete):
        # Arrange
        event = {'body': '{"subscription_id": "test_subscription_id"}', 'headers': {'Authorization': 'test_token'}}
        mock_db_manager.return_value.fetch_one.return_value = ['email']
        mock_verify_id_token.return_value = {'uid': 'uid'}
        mock_subscription_retrieve.return_value = MagicMock(customer_email='email')

        # Act
        cancel_subscription = CancelSubscription(event)
        response = cancel_subscription.cancel_subscription()

        # Assert
        mock_verify_id_token.assert_called_once_with('test_token')
        mock_db_manager.return_value.fetch_one.assert_called_once_with("SELECT email FROM users WHERE uid = %s", ('uid',))
        mock_subscription_retrieve.assert_called_once_with('test_subscription_id')
        mock_subscription_delete.assert_called_once_with('test_subscription_id')
        expected_message = {'message': 'Subscription canceled successfully!'}
        self.assertEqual(json.loads(response['body']['message']), expected_message)

        print("Cancel UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()