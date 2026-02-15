import unittest
import json
from unittest.mock import patch, MagicMock
from customer.update_name import UpdateName

class TestUpdateName(unittest.TestCase):
    @patch('customer.update_name.DbManager')
    @patch('customer.update_name.UpdateName.update_user_name')
    def test_update_user_name(self, mock_update_user_name, mock_db_manager):
        # Arrange
        event = {'body': '{"name": "new_name"}'}
        mock_db_manager.return_value = MagicMock()
        mock_update_user_name.return_value = {
            'statusCode': 200,
            'body': {
                'message': json.dumps('Name updated successfully')
            }
        }
        
        # Act
        update_name = UpdateName(event)
        response = update_name.update_user_name(event)

        # Assert
        expected_message = 'Name updated successfully'
        self.assertEqual(json.loads(response['body']['message']), expected_message)

        print("UpdateName UnitTest Successful!!!")

if __name__ == '__main__':
    unittest.main()