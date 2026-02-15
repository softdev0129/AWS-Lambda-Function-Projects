from utils.build_response import build_response
from db.plf_db_manager import PlfDbManager


def get_extract_file():
    db_manager = PlfDbManager()

    # Initialize an empty payload
    response_payload = {}

    try:
        # Query to fetch data from the database
        query = """
            SELECT
                industry,
                extract_time,
                ARRAY_AGG(id) AS id_list,
                title
            FROM international_extract
            WHERE extract_time >= date_trunc('week', current_date) - interval '6 weeks'
            GROUP BY industry, extract_time, title
            ORDER BY extract_time DESC;
        """

        # Execute the query
        rows = db_manager.fetch_all(query)

        # Iterate through the fetched rows and populate response_payload dynamically
        for row in rows:
            industry = row[0].replace(" ", "_")
            id = row[2]
            if industry not in response_payload:
                response_payload[industry] = []
            obj = {"ids": id, "name": row[3]}
            if len(response_payload[industry]) < 5:
                response_payload[industry].append(obj)

        # Commit the transaction
        db_manager.close()

    except Exception as e:
        print(e)
        return build_response(500, {"error": str(e)})

    # Return the response payload as JSON
    return build_response(200, response_payload)
