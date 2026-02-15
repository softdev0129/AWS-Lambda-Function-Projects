import requests
import json
import logging
import time
import random
import pg8000
from datetime import datetime
from math import cos, sin, sqrt, pi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Database connection details
db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_port = 5432  # Default PostgreSQL port
db_database = 'scraper_db'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'

def create_tables_if_not_exist():
    conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
    cursor = conn.cursor()
    
    executions_schema = """
        CREATE TABLE IF NOT EXISTS executions (
            id SERIAL PRIMARY KEY,
            search_string TEXT,
            location_query TEXT,
            status TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration INTERVAL,
            records_found INTEGER,
            results JSONB
        );
    """
    
    cursor.execute(executions_schema)
    conn.commit()
    conn.close()

def update_execution_status(execution_id, status, end_time=None, records_found=None, results=None):
    conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
    cursor = conn.cursor()

    if end_time:
        cursor.execute("""
            UPDATE executions
            SET status = %s, end_time = %s, duration = end_time - start_time, records_found = %s, results = %s
            WHERE id = %s
        """, (status, end_time, records_found, json.dumps(results), execution_id))
    else:
        cursor.execute("""
            UPDATE executions
            SET status = %s, results = %s
            WHERE id = %s
        """, (status, json.dumps(results), execution_id))
    
    conn.commit()
    conn.close()

def start_execution(search_string, location_query):
    conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
    cursor = conn.cursor()

    start_time = datetime.utcnow()
    status = 'RUNNING'
    cursor.execute("""
        INSERT INTO executions (search_string, location_query, status, start_time)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (search_string, location_query, status, start_time))

    execution_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    return execution_id, start_time

def random_point_within_radius(lat, lng, radius_in_meters):
    radius_in_degrees = radius_in_meters / 111320  # 1 degree latitude ≈ 111.32 km
    r = radius_in_degrees * sqrt(random.uniform(0, 1))
    theta = random.uniform(0, 2 * pi)
    offset_lat = r * cos(theta)
    offset_lng = r * sin(theta) / cos(lat * pi / 180)
    return lat + offset_lat, lng + offset_lng

def get_place_details(search_string, location_query, api_key, page_token=None):
    logger.info(f"Getting place details for search string: {search_string} and location: {location_query}")

    place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    nearbysearch_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # Convert location query to latitude and longitude
    geocode_params = {
        'address': location_query,
        'key': api_key
    }
    geocode_response = requests.get(geocode_url, params=geocode_params)
    if geocode_response.status_code != 200:
        logger.error(f"Geocode API request failed with status code: {geocode_response.status_code}")
        return None, None

    geocode_result = geocode_response.json()
    if 'results' not in geocode_result or not geocode_result['results']:
        logger.error("No results found for the geocode query.")
        return None, None

    location = geocode_result['results'][0]['geometry']['location']
    latitude = location["lat"]
    longitude = location["lng"]

    # Generate random location within a 50 km radius
    randomized_latitude, randomized_longitude = random_point_within_radius(latitude, longitude, 50000)
    logger.info(f"Original location: ({latitude}, {longitude}), Randomized location: ({randomized_latitude}, {randomized_longitude})")

    # Search for places nearby using the nearbysearch API
    nearbysearch_params = {
        'location': f"{randomized_latitude},{randomized_longitude}",
        'radius': 50000,  # Increased radius to 50 kilometers
        'keyword': search_string,
        'key': api_key
    }
    if page_token:
        nearbysearch_params['pagetoken'] = page_token

    response = requests.get(nearbysearch_url, params=nearbysearch_params)
    if response.status_code != 200:
        logger.error(f"Nearby Search API request failed with status code: {response.status_code}")
        return None, None

    result = response.json()
    if 'results' not in result or not result['results']:
        logger.error("No results found for the nearby search.")
        return None, None

    places_info = []
    for candidate in result['results']:
        place_id = candidate['place_id']
        logger.info(f"Found place ID: {place_id}")

        details_params = {
            'place_id': place_id,
            'fields': 'name,rating,user_ratings_total,formatted_address,website,formatted_phone_number,types,url',
            'key': api_key
        }

        details_response = requests.get(place_details_url, params=details_params)
        if details_response.status_code != 200:
            logger.error(f"Place Details API request failed with status code: {details_response.status_code}")
            continue

        details_result = details_response.json()
        if 'result' not in details_result:
            logger.error("No result found for place details.")
            continue

        place = details_result['result']
        address_components = place.get('formatted_address', '').split(', ')
        street = address_components[0] if len(address_components) > 0 else None
        city = address_components[1] if len(address_components) > 1 else None
        state = address_components[2] if len(address_components) > 2 else None
        country_code = address_components[3] if len(address_components) > 3 else None

        places_info.append({
            'title': place.get('name'),
            'totalScore': place.get('rating'),
            'reviewsCount': place.get('user_ratings_total'),
            'street': street,
            'city': city,
            'state': state,
            'countryCode': country_code,
            'website': place.get('website'),
            'phone': place.get('formatted_phone_number'),
            'categoryName': place.get('types')[0] if place.get('types') else None,
            'url': place.get('url')
        })
        logger.info(f"Added place: {place.get('name')}")

    next_page_token = result.get('next_page_token')
    return places_info, next_page_token

def get_places_info(search_strings_array, location_query, api_key, webhook_url):
    places_info = []
    create_tables_if_not_exist()
    for search_string in search_strings_array:
        logger.info(f"Processing search string: {search_string}")
        execution_id, start_time = start_execution(search_string, location_query)
        page_token = None
        total_records = 0
        all_results = []
        try:
            while True:
                place_info_list, page_token = get_place_details(search_string, location_query, api_key, page_token)
                if place_info_list:
                    total_records += len(place_info_list)
                    all_results.extend(place_info_list)
                    for place_info in place_info_list:
                        places_info.append(place_info)
                        # send_to_webhook(place_info, webhook_url)
                if not page_token:
                    break
                # Wait for a few seconds to let the next page token become active
                time.sleep(2)
            update_execution_status(execution_id, 'COMPLETED', datetime.utcnow(), total_records, all_results)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            update_execution_status(execution_id, 'FAILED', datetime.utcnow(), total_records, all_results)
    return places_info

def send_to_webhook(data, webhook_url):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        logger.info("Data successfully sent to webhook.")
    else:
        logger.error(f"Failed to send data to webhook. Status code: {response.status_code}")
