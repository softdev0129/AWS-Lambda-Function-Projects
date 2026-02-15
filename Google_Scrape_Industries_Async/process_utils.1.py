import json
import requests
import traceback
from apify_client import ApifyClient

def process_data(body):
    conn = None
    try:
        # Database connection details (reused from main)
        db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
        db_port = 5432  # Default PostgreSQL port
        db_database = 'scraper_db'
        db_user = 'postgres'
        db_password = 'GWtxSGM4swxxhN3fMHRH'
        
        # Connect to the database
        conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
        
        # Create tables if they do not exist
        create_tables_if_not_exist(conn)

        # Insert data into the results table
        cursor = conn.cursor()
        # Iterate through items in the dataset and insert into the database
        defaultDatasetId = body.get('resource', {}).get('defaultDatasetId')
        
        # Initialize ApifyClient with your API token
        apify_client = ApifyClient("apify_api_wV8knzAbg6CPxsQe1gHRP82QZOydWb1pnGf5")

        total_records = 0
        successful_inserts = 0

        for item in apify_client.dataset(defaultDatasetId).iterate_items():
            total_records += 1
            print(item)
            title = item.get('title')
            if title is None:
                continue
            total_score = item.get('totalScore')
            reviews_count = item.get('reviewsCount')
            street = item.get('street')
            city = item.get('city')
            state = item.get('state')
            country_code = item.get('countryCode')
            website = item.get('website')
            phone = item.get('phone')
            category_name = item.get('categoryName')
            url = item.get('url')
        
            try:
                # Insert data into the database
                cursor.execute("""
                    INSERT INTO public.results (title, total_score, reviews_count, street, city, state, country_code, website, phone, category_name, url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, total_score, reviews_count, street, city, state, country_code, website, phone, category_name, url))
                # Commit after each successful insert
                conn.commit()
                successful_inserts += 1
            except Exception as e:
                # Check for specific SQLSTATE codes for integrity errors
                print(f"Database error: {e}")
                conn.rollback()
                continue

        # Update count in google_search_query table
        update_search_query_count(conn)

        print(f"Total records processed: {total_records}")
        print(f"Total records successfully inserted: {successful_inserts}")

        return {
            'statusCode': 200,
            'body': f'Data processed successfully. Total: {total_records}, Inserted: {successful_inserts}.'
        }
    except Exception as e:
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}',
            'stackTrace': traceback.format_exc()
        }
    finally:
        if conn:
            conn.close()
