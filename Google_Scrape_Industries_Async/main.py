import os
import json
import pg8000
import traceback
from db_utils import create_tables_if_not_exist, get_random_search_query
from google_places import get_places_info
from process_utils import process_data
from apify_utils import start_apify_actor
from jobqueue_tracker import start_job_event, complete_job_event, fail_job_event

# Database connection details
db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_port = os.environ.get('DB_PORT', 5432)  # Default PostgreSQL port
db_database = 'scraper_db'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'

event_name = 'Google_Scraper'

def lambda_handler(event, context):
    conn = None
    try:
        job_id = None
        # Retrieve action from request payload
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', event.get('action'))
        if not action:
            return {
                'statusCode': 400,
                'body': f'Action not provided in request payload. {body}'
            }
        
        # Connect to the database
        conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
        
        # Create tables if they do not exist
        create_tables_if_not_exist(conn)
        
        if action == 'start_apify_actor':
            job_id = start_job_event(f'{event_name}::{action.upper()}')
            # Get random search query from database
            search_query = get_random_search_query(conn)
            if not search_query:
                return {
                    'statusCode': 500,
                    'body': 'No search query found in the database.'
                }
            
            # Prepare input for Actor
            run_input = {
                "searchStringsArray": search_query["searchStringsArray"],
                "locationQuery": search_query["locationQuery"],
                "maxCrawledPlacesPerSearch": search_query["maxCrawledPlacesPerSearch"],
                # Add other parameters as needed
            }
            
            # Start the Actor
            start_apify_actor(run_input)
            complete_job_event(job_id)
            return {
                'statusCode': 200,
                'body': 'Actor job started successfully.'
            }
        elif action == 'process_data':
            job_id = start_job_event(f'{event_name}::{action.title()}')
            # Process data synchronously
            response = process_data()
            complete_job_event(job_id)
            return response
        elif action == 'start_job':
            job_id = start_job_event(f'{event_name}::{action.title()}')
            # Get random search query from database
            search_query = get_random_search_query(conn)
            if not search_query:
                complete_job_event(job_id)
                return {
                    'statusCode': 500,
                    'body': 'No search query found in the database.'
                }
            
            # Fetch place information from Google Places API
            search_strings_array = search_query["searchStringsArray"]
            location_query = search_query["locationQuery"]
            webhook_url = 'https://swr5cg4vp0.execute-api.eu-west-1.amazonaws.com/prod/process'
            api_key = 'AIzaSyArYxkdYVXGNA3UW3kCQ-0PIVpgOwDxjtw'  # Replace with your actual Google API key

            places_info = get_places_info(search_strings_array, location_query, api_key, webhook_url)
            complete_job_event(job_id)
            return {
                'statusCode': 200,
                'body': json.dumps(places_info)
            }
        else:
            return {
                'statusCode': 400,
                'body': f'Invalid action: {action}.'
            }
    except Exception as e:
        fail_job_event(job_id)
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}',
            'stackTrace': traceback.format_exc()
        }
    finally:
        if conn:
            conn.close()
