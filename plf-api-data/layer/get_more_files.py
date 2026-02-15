from db.plf_db_manager import PlfDbManager
from utils.build_response import build_response

def get_more_file(industry):
    industry = industry.replace("_", " ")
    db_manager = PlfDbManager()
    response_payload = {}
    try:
        query = """
            SELECT
                industry,
                to_char(extract_time, 'DD-MM-YYYY') AS formatted_extract_time,
                to_char(extract_time, 'MM') AS mon,
                ARRAY_AGG(id) AS id_list,
                title
            FROM international_extract
            WHERE industry = %s
            GROUP BY industry, formatted_extract_time, mon, title
            ORDER BY mon DESC, formatted_extract_time DESC;
        """
        rows = db_manager.fetch_all(query, (industry,))
        for row in rows:
            mon = row[2]
            id_list = row[3]
            if mon not in response_payload:
                response_payload[mon] = []
            obj = {"ids": id_list, "name": row[4]}
            response_payload[mon].append(obj)
    except Exception as e:
        return build_response(500, {"error": str(e)})
    return build_response(200, response_payload)
