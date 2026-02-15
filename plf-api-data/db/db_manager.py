import pg8000
import os


class DbManager:
    def __init__(self):
        self.connection = pg8000.connect(
            user=os.environ['RDS_USERNAME'],
            password=os.environ['RDS_PASSWORD'],
            host=os.environ['RDS_ENDPOINT'],
            database="scraper_db"
        )

    def execute_query(self, query, params=None):
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


# Example usage
if __name__ == "__main__":
    scraper_db_manager = DbManager()
    scraper_db_manager.close()
