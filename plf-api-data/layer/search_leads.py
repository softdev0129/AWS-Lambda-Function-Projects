from utils.build_response import build_response
from db.plf_db_manager import PlfDbManager


class SearchLeads:
    def __init__(self):
        self.db_manager = PlfDbManager()

    def search_leads(self, keyword):
        response_payload = {}
        try:
            query = f"""
                        SELECT
                            industry,
                            to_char(extract_time, 'DD-MM-YYYY') AS formatted_extract_time,
                            ARRAY_AGG(id) AS id_list
                        FROM locale_extract 
                        WHERE title like '%{keyword}%'
                        GROUP BY industry, formatted_extract_time
                        ORDER BY formatted_extract_time DESC;
                    """
            rows = self.db_manager.fetch_all(query)
            for row in rows:
                industry = row[0].replace(" ", "_")
                extract_time = row[1]
                id = row[2]
                if industry not in response_payload:
                    response_payload[industry] = []
                obj = {"ids": id, "name": f'{extract_time}_{industry.lower()}_leads', 'type': 'local'}
                response_payload[industry].append(obj)

            query = f"""
                            SELECT
                                industry,
                                to_char(extract_time, 'DD-MM-YYYY') AS formatted_extract_time,
                                ARRAY_AGG(id) AS id_list
                            FROM international_extract 
                            WHERE title like '%{keyword}%'
                            GROUP BY industry, formatted_extract_time
                            ORDER BY formatted_extract_time DESC;
                    """
            rows = self.db_manager.fetch_all(query)
            for row in rows:
                industry = row[0].replace(" ", "_")
                extract_time = row[1]
                id = row[2]
                if industry not in response_payload:
                    response_payload[industry] = []
                obj = {"ids": id, "name": f'{extract_time}_{industry.lower()}_leads', 'type': 'international'}
                response_payload[industry].append(obj)
            self.db_manager.close()
            return build_response(200, response_payload)
        except Exception as e:
            return build_response(400, {'error': str(e)})
