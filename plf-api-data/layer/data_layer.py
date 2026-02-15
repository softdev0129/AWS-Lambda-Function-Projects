import pg8000
import os

class DataLayer:
    def __init__(self):
        self.conn = pg8000.connect(
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME')
        )
    
    def get_internation_email(self):
        try:
            query = "SELECT email FROM international_bulk_selection"
            email = self.db_manager.fetch_one(query)
            self.db_manager.close()
            
        except Exception as e:
            return build_response(400, {'error': str(e)})
    
    def get_internation_number(self):
        try:
            query = "SELECT number FROM international_bulk_selection"
            email = self.db_manager.fetch_one(query)
            self.db_manager.close()
            
        except Exception as e:
            return build_response(400, {'error': str(e)})

    def get_locale_email(self):
        try:
            query = "SELECT email FROM locale_bulk_selection WHERE locale = %s"
            email = self.db_manager.fetch_one(query)
            self.db_manager.close()
            
        except Exception as e:
            return build_response(400, {'error': str(e)})

    def get_locale_number(self):
        try:
            query = "SELECT number FROM locale_bulk_selection WHERE locale = %s"
            email = self.db_manager.fetch_one(query)
            self.db_manager.close()
            
        except Exception as e:
            return build_response(400, {'error': str(e)})

    def get_serviced_links(self):
        try:
            query = "SELECT number FROM serviced_links_directoy WHERE locale = %s"
            email = self.db_manager.fetch_one(query)
            self.db_manager.close()
            
        except Exception as e:
            return build_response(400, {'error': str(e)})