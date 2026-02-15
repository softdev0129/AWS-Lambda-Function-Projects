import unittest
import json
from unittest.mock import patch, MagicMock
from billing.buy_subscription import BuySubscription

class TestBuySubscription(unittest.TestCase):
    @patch('stripe.Subscription.create')
    @patch('stripe.Customer.create')
    @patch('stripe.Customer.list')
    @patch('firebase_admin.auth.verify_id_token')
    @patch('billing.buy_subscription.DbManager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'mock_value'}, clear=True)
    def test_create_subscription(self, mock_db_manager, mock_verify_id_token, mock_customer_list, mock_customer_create, mock_subscription_create):
        # Arrange
        event = {'body': '{"payment_method_id": "test_method_id", "price_id": "test_price_id"}', 'headers': {'Authorization': 'test_token'}}
        mock_db_manager.return_value.fetch_one.return_value = ['email']
        mock_verify_id_token.return_value = {'uid': 'uid'}
        mock_customer_list.return_value.data = []
        mock_customer_create.return_value = MagicMock(id='customer_id')
        mock_subscription_create.return_value = MagicMock(id='subscription_id', latest_invoice=MagicMock(payment_intent=MagicMock(client_secret='client_secret')))

        # Act
        buy_subscription = BuySubscription(event)
        response = buy_subscription.create_subscription()

        # Assert
        mock_verify_id_token.assert_called_once_with('test_token')
        mock_db_manager.return_value.fetch_one.assert_called_once_with("SELECT email FROM users WHERE uid = %s", ('uid',))
        mock_customer_list.assert_called_once_with(email='email')
        mock_customer_create.assert_called_once_with(email='email', payment_method='test_method_id', invoice_settings={'default_payment_method': 'test_method_id'})
        mock_subscription_create.assert_called_once_with(customer='customer_id', items=[{'price': 'test_price_id'}], expand=['latest_invoice.payment_intent'])
        expected_message = {'subscription_id': 'subscription_id', 'client_secret': 'client_secret'}
        self.assertEqual(json.loads(response['body']['message']), expected_message)

        print("Buy UnitTest Successful!!!")


if __name__ == '__main__':
    unittest.main()