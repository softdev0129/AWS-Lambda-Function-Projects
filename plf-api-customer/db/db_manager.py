import pg8000
import os


class DbManager:
    def __init__(self):
        self.connection = pg8000.connect(
            user=os.environ['RDS_USERNAME'],
            password=os.environ['RDS_PASSWORD'],
            host=os.environ['RDS_ENDPOINT'],
            database=os.environ['RDS_DB_NAME']
        )
        self.create_tables_if_not_exist()

    def execute_query(self, query, params=None):
        print(f"Connected to Database - {os.environ['RDS_DB_NAME']}")
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        self.connection.commit()
        cursor.close()

    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def close(self):
        self.connection.close()

    def create_tables_if_not_exist(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            uid VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            account_name VARCHAR(255),
            billing_credit_id VARCHAR(255),
            billing_subscription_id  VARCHAR(255)
        );
        """
        # Add more table creation queries here as needed

        self.execute_query(create_users_table)
        # Execute more table creation queries here as needed

    def update_user_name(self, uid, new_name):
        update_query = "UPDATE users SET account_name = %s WHERE uid = %s"
        self.execute_query(update_query, (new_name, uid))
    
    def get_user(self, uid):
        query = "SELECT id as user_id, email, stripe_customer_id, billing_credit_id FROM users WHERE uid = %s"
        result = self.fetch_one(query, (uid,))
        return {
            'user_id': result[0],
            'email': result[1],  # Assuming product_id is at index 5
            'stripe_customer_id': result[2],  # Assuming product_id is at index 5
            'billing_credit_id': result[3],  # Assuming product_id is at index 5
        }


# Example usage
if __name__ == "__main__":
    db_manager = DbManager()
    db_manager.close()
