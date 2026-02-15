import json
import time
import random
import psycopg2
import requests
from psycopg2.extras import DictCursor
import traceback
from fiverr_api.scrapers import gig_scrape

# Function to establish database connection
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname='scraper_db',
            user='postgres',
            password='GWtxSGM4swxxhN3fMHRH',
            host='database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com',
        )
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)

# Function to create 'gigs' table if it doesn't exist
def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gigs_review (
                id SERIAL PRIMARY KEY,
                review_id VARCHAR(255),
                comment TEXT,
                comment_language VARCHAR(2),
                username VARCHAR(255),
                reviewer_country_code VARCHAR(2),
                user_image_url TEXT,
                created_at TIMESTAMP,
                value INT,
                reviewer_country VARCHAR(255),
                encrypted_order_id VARCHAR(255),
                score FLOAT,
                reviewer_industry TEXT,
                repeat_buyer BOOLEAN,
                is_business BOOLEAN,
                gig_id BIGINT,
                relevancy_score FLOAT,
                price_range_start INT,
                price_range_end INT,
                reviews_count_as_buyer INT,
                is_cancelled_order BOOLEAN,
                original_relevancy_score FLOAT
            )
        """)
        conn.commit()
        cursor.close()
    except psycopg2.Error as e:
        print("Error creating table:", e)

# Function to insert data into the database
def insert_data(conn, gigs_data):
    try:
        cursor = conn.cursor()
        for gig_data in gigs_data:
            for review in gig_data['reviews']:
                cursor.execute("""
                INSERT INTO gigs_review (review_id, comment, comment_language, username, reviewer_country_code,
                    user_image_url, created_at, value, reviewer_country, encrypted_order_id,
                    score, reviewer_industry, repeat_buyer, is_business, gig_id,
                    relevancy_score, price_range_start, price_range_end, reviews_count_as_buyer,
                    is_cancelled_order, original_relevancy_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    review.get('id', ''), # Assuming 'default_review_id' is your default value
                    review.get('comment', 'No comment'), # Assuming 'No comment' as default
                    review.get('comment_language', 'EN'), # Default language EN
                    review.get('username', 'Anonymous'), # Default username
                    review.get('reviewer_country_code', 'XX'), # Default country code
                    review.get('user_image_url', 'default_url'), # Default image URL
                    review.get('created_at', '1970-01-01 00:00:00'), # Default timestamp, adjust as necessary
                    review.get('value', 0), # Default value
                    review.get('reviewer_country', ''), # Default country
                    review.get('encrypted_order_id', ''), # Default order ID
                    review.get('score', 0.0), # Default score
                    ', '.join(review.get('reviewer_industry', [])), # Handles list or default empty list
                    review.get('repeat_buyer', False), # Default boolean
                    review.get('is_business', False), # Default boolean
                    review.get('gig_id', 0), # Default gig ID
                    review.get('relevancy_score', 0.0), # Default relevancy score
                    review.get('price_range_start', 0), # Default start price
                    review.get('price_range_end', 0), # Default end price
                    review.get('reviews_count_as_buyer', 0), # Default reviews count
                    review.get('is_cancelled_order', False), # Default boolean
                    review.get('original_relevancy_score', 0.0) # Default original relevancy score
                ))
        conn.commit()
        cursor.close()
    except psycopg2.Error as e:
        print("Error inserting data:", e)
        traceback.print_exc()

# Function to sleep for a random duration
def sleep_random(min_duration, max_duration):
    sleep_duration = random.uniform(min_duration, max_duration)
    time.sleep(sleep_duration)

def lambda_handler(event, context):
    ipaddres = requests.get('http://checkip.amazonaws.com').text.rstrip()
    print(ipaddres)
    # Establish database connection
    conn = connect_to_db()

    if conn is None:
        return {
            "statusCode": 500,
            "body": "Failed to connect to the database"
        }

    # Create 'gigs' table if it doesn't exist
    create_table(conn)

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM fiverr_gig_web ORDER BY RANDOM() LIMIT 5")  # Adjust for your DBMS
            gigs_data = cursor.fetchall()  # Fetches the gigs data
    except Exception as e:
        conn.close()
        return {
            "statusCode": 500,
            "body": "Failed to retrieve data: " + str(e)
        }

    for i in range(len(gigs_data)):
        print(gigs_data[i])
        gig_data = gig_scrape(f"https://www.fiverr.com{gigs_data[i]['gig_url']}")
        gigs_data[i] = gig_data['perseus_initial_props']['reviews']

    # Insert data into the database
    insert_data(conn, gigs_data)

    # Close database connection
    conn.close()

    return {
        "statusCode": 200,
        "body": "Data inserted successfully"
    }
