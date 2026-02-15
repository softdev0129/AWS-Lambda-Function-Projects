import unittest
import json
from unittest.mock import patch, MagicMock
from billing.get_billing_history import GetBillingHistory # replace 'billing.get_billing_history' with the actual module name

class TestGetBillingHistory(unittest.TestCase):
    @patch('stripe.Invoice.list')
    @patch('stripe.Customer.list')
    @patch('firebase_admin.auth.verify_id_token')
    @patch('billing.get_billing_history.DbManager') # replace 'billing.get_billing_history' with the actual module name
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'mock_value'}, clear=True)
    def test_fetch_billing_history(self, mock_db_manager, mock_verify_id_token, mock_customer_list, mock_invoice_list):
        # Arrange
        event = {'headers': {'Authorization': 'test_token'}}
        mock_db_manager.return_value.fetch_one.return_value = ['email']
        mock_verify_id_token.return_value = {'uid': 'uid'}
        mock_customer = MagicMock()
        mock_customer.id = 'customer_id'
        mock_customer_list.return_value.data = [mock_customer]

        mock_invoice = MagicMock()
        mock_invoice.id = 'invoice_id'
        mock_invoice.amount_due = 100
        mock_invoice.amount_paid = 100
        mock_invoice.amount_remaining = 0
        mock_invoice.currency = 'usd'
        mock_invoice.description = 'test_description'
        mock_invoice.status = 'paid'
        mock_invoice.period_start = 'test_start'
        mock_invoice.period_end = 'test_end'
        mock_invoice.due_date = 'test_due_date'
        mock_invoice.paid = True
        mock_invoice_list.return_value.auto_paging_iter.return_value = [mock_invoice]

        # Act
        get_billing_history = GetBillingHistory(event)
        response = get_billing_history.fetch_billing_history()

        # Assert
        mock_verify_id_token.assert_called_once_with('test_token')
        mock_db_manager.return_value.fetch_one.assert_called_once_with("SELECT email FROM users WHERE uid = %s", ('uid',))
        mock_customer_list.assert_called_once_with(email='email')
        mock_invoice_list.assert_called_once_with(customer='customer_id')

        expected_message = {'billing_history': [{'id': 'invoice_id', 'amount_due': 100, 'amount_paid': 100, 'amount_remaining': 0, 'currency': 'usd', 'description': 'test_description', 'status': 'paid', 'period_start': 'test_start', 'period_end': 'test_end', 'due_date': 'test_due_date', 'paid': True}]}
        self.assertEqual(json.loads(response['body']['message']), expected_message)

        print("Fetch Billing History UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()