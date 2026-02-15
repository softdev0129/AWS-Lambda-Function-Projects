import os
import json
import random
import pg8000
from apify_client import ApifyClient

# Initialize ApifyClient with your API token
apify_client = ApifyClient("apify_api_wV8knzAbg6CPxsQe1gHRP82QZOydWb1pnGf5")

# Database connection details
db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_port = os.environ.get('DB_PORT', 5432)  # Default PostgreSQL port
db_database = 'scraper_db'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'

def create_tables_if_not_exist(conn):
    # Define the table schemas
    google_search_query_schema = """
        CREATE TABLE IF NOT EXISTS google_search_query (
            id SERIAL PRIMARY KEY,
            search_strings_array TEXT[],
            location_query TEXT,
            max_crawled_places_per_search INTEGER,
            count INTEGER DEFAULT 0
        )
    """
    results_schema = """
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            title TEXT,
            total_score NUMERIC,
            reviews_count INTEGER,
            street TEXT,
            city TEXT,
            state TEXT,
            country_code TEXT,
            website TEXT,
            phone TEXT,
            category_name TEXT,
            url TEXT
        )
    """
    cursor = conn.cursor()
    cursor.execute(google_search_query_schema)
    cursor.execute(results_schema)
    conn.commit()

def get_random_search_query(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT search_strings_array, location_query, max_crawled_places_per_search FROM google_search_query ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    if row:
        return {
            "searchStringsArray": row[0],
            "locationQuery": row[1],
            "maxCrawledPlacesPerSearch": row[2]
        }
    return None

def update_search_query_count(conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE google_search_query SET count = count + 1 WHERE id = (SELECT id FROM google_search_query ORDER BY RANDOM() LIMIT 1)")
    conn.commit()

def lambda_handler(event, context):
    conn = None
    try:
        # Connect to the database
        conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
        
        # Create tables if they do not exist
        create_tables_if_not_exist(conn)
        
        # Get random search query from database
        search_query = get_random_search_query(conn)
        if not search_query:
            return {
                'statusCode': 500,
                'body': 'No search query found in the database.'
            }
        
        # Run the Actor and wait for it to finish
        run_input = {
            "searchStringsArray": search_query["searchStringsArray"],
            "locationQuery": search_query["locationQuery"],
            "maxCrawledPlacesPerSearch": search_query["maxCrawledPlacesPerSearch"],
            "language": "en",
            "maxImages": 1,
            "scrapeImageAuthors": False,
            "onlyDataFromSearchPage": False,
            "includeWebResults": False,
            "scrapeDirectories": False,
            "deeperCityScrape": False,
            "maxReviews": None,
            "reviewsSort": "newest",
            "reviewsFilterString": "",
            "scrapeReviewerName": True,
            "scrapeReviewerId": True,
            "scrapeReviewerUrl": True,
            "scrapeReviewId": True,
            "scrapeReviewUrl": True,
            "scrapeResponseFromOwnerText": True,
            "maxQuestions": None,
            "countryCode": None,
            "searchMatching": "all",
            "placeMinimumStars": "",
            "skipClosedPlaces": False,
            "allPlacesNoSearchAction": "",
        }

        # Run the Actor and wait for it to finish
        run = apify_client.actor("nwua9Gu5YrADL7ZDj").call(run_input=run_input)

        # Insert data into the results table
        cursor = conn.cursor()
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            data = json.loads(item['data'])
            title = data.get('title')
            total_score = data.get('totalScore')
            reviews_count = data.get('reviewsCount')
            street = data.get('street')
            city = data.get('city')
            state = data.get('state')
            country_code = data.get('countryCode')
            website = data.get('website')
            phone = data.get('phone')
            category_name = data.get('categoryName')
            url = data.get('url')

            cursor.execute("""
                INSERT INTO results (title, total_score, reviews_count, street, city, state, country_code, website, phone, category_name, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, total_score, reviews_count, street, city, state, country_code, website, phone, category_name, url))
        
        conn.commit()

        # Update count in google_search_query table
        update_search_query_count(conn)
        
        return {
            'statusCode': 200,
            'body': 'Data stored successfully in the database.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
    finally:
        if conn:
            conn.close()
