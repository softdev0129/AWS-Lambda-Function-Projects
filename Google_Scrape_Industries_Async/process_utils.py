import json
import requests
import traceback
import pg8000

def create_tables_if_not_exist(conn):
    # Define the table schema for executions if it does not exist
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
            results JSONB,
            is_processed BOOLEAN DEFAULT FALSE
        );
    """
    cursor = conn.cursor()
    cursor.execute(executions_schema)
    conn.commit()

def update_search_query_count(conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE google_search_query SET count = count + 1 WHERE id = (SELECT id FROM google_search_query ORDER BY RANDOM() LIMIT 1)")
    conn.commit()

def process_data():
    conn = None
    try:
        # Database connection details
        db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
        db_port = 5432  # Default PostgreSQL port
        db_database = 'scraper_db'
        db_user = 'postgres'
        db_password = 'GWtxSGM4swxxhN3fMHRH'
        
        # Connect to the database
        conn = pg8000.connect(host=db_host, port=db_port, database=db_database, user=db_user, password=db_password)
        
        # Create tables if they do not exist
        create_tables_if_not_exist(conn)

        # Fetch unprocessed data from the executions table
        cursor = conn.cursor()
        cursor.execute("SELECT id, results FROM executions WHERE is_processed = FALSE AND results IS NOT NULL")
        rows = cursor.fetchall()

        total_records = 0
        successful_inserts = 0

        for row in rows:
            execution_id, results = row
            items = results
            for item in items:
                total_records += 1
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
                    # Insert data into the results table
                    cursor.execute("""
                        INSERT INTO public.results (title, total_score, reviews_count, street, city, state, country_code, website, phone, category_name, url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (title, total_score, reviews_count, street, city, state, country_code, website, phone, category_name, url))
                    # Commit after each successful insert
                    conn.commit()
                    successful_inserts += 1
                except Exception as e:
                    print(f"Database error: {e}")
                    conn.rollback()
                    continue

            # Mark the execution as processed
            cursor.execute("UPDATE executions SET is_processed = TRUE WHERE id = %s", (execution_id,))
            conn.commit()

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

# Example usage
response = process_data()
print(response)
