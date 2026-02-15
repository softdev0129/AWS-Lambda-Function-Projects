from utils.build_response import build_response
from db.plf_db_manager import PlfDbManager


class LocalLeads:
    def __init__(self):
        self.db_manager = PlfDbManager()

    def get_local_leads(self, locations):
        response_payload = {}
        try:
            location = locations.split(',')
            search_text = ''
            if location is not None:
                for l in location:
                    if search_text == '':
                        search_text = " AND (city = '" + l + "'"
                    else:
                        search_text += " OR city = '" + l + "'"
            if search_text != '':
                search_text += ')'
            query = f"""
                        SELECT
                            industry,
                            extract_time,
                            ARRAY_AGG(id) AS id_list,
                            title
                        FROM locale_extract
                        WHERE extract_time >= date_trunc('week', current_date) - interval '6 weeks' {search_text}
                        GROUP BY industry, extract_time, title
                        ORDER BY extract_time DESC;
                    """
            rows = self.db_manager.fetch_all(query)
            self.db_manager.close()
            for row in rows:
                industry = row[0].replace(" ", "_")
                id = row[2]
                if industry not in response_payload:
                    response_payload[industry] = []
                obj = {"ids": id, "name": row[3]}
                if len(response_payload[industry]) < 5:
                    response_payload[industry].append(obj)
            return build_response(200, response_payload)
        except Exception as e:
            return build_response(400, {'error': str(e)})
