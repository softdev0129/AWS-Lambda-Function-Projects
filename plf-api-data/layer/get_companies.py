from utils.build_response import build_response
from db.db_manager import DbManager


def fetch_companies():
    try:
        scraper_db_manager = DbManager()

        # Query to get distinct category_name from results table
        query_category = "SELECT DISTINCT(category_name) FROM results"
        category_rows = scraper_db_manager.fetch_all(query_category)

        # Query to get distinct location_query from executions table
        query_location = "SELECT DISTINCT(location_query) FROM executions"
        location_rows = scraper_db_manager.fetch_all(query_location)

        scraper_db_manager.close()

        # Extract companies (category names)
        companies = [row[0] for row in category_rows]

        # Extract distinct locations (location queries)
        locations = [row[0] for row in location_rows]

        # Build the response
        return build_response(200, {'companies': companies, 'cities': locations})

    except Exception as e:
        return build_response(400, {'error': str(e)})

