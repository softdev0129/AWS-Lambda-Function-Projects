import pg8000

def create_tables_if_not_exist(conn):
    # Define the table schema for results
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
