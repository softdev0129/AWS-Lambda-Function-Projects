import json
import requests
import psycopg2
import traceback
import time
import random
from bs4 import BeautifulSoup
from psycopg2.extras import DictCursor

class DatabaseConnector:
    def __init__(self, host, user, password, dbname):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.connection = None
        self.cursor = None
    
    def connect(self):
        self.connection = psycopg2.connect(host=self.host, user=self.user, password=self.password, dbname=self.dbname)
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

class WebScraper:
    def __init__(self, headers):
        self.session = requests.session()
        self.session.headers = headers
    
    def headless_request(self, url):
        res = self.session.get(url)
        if res.status_code != 200:
            raise Exception(f"Failed to fetch data. Status code: {res.status_code}")
        return res.text

class LambdaHandler:
    def __init__(self, db_config, headers):
        self.db_connector = DatabaseConnector(db_config['host'], db_config['user'], db_config['password'], db_config['dbname'])
        self.web_scraper = WebScraper(headers)

    # Function to sleep for a random duration
    def sleep_random(self, min_duration, max_duration):
        sleep_duration = random.uniform(min_duration, max_duration)
        time.sleep(sleep_duration)

    def fetch_and_store_gigs(self, payload):
        conn = self.db_connector.connection
        cursor = self.db_connector.cursor

        cat = payload['category_name']
        sub_cat = payload['sub_cat_name']
        url = "https://www.fiverr.com/categories/%s/%s?source=pagination&page=%s&offset=%s" % (cat, sub_cat, payload['page'], 0)
        record_count = self.get_record_count(sub_cat)

        response = self.web_scraper.headless_request(url)

        soup = BeautifulSoup(response, 'html.parser')
        script_tag = soup.find('script', {'id': 'perseus-initial-props'})
        json_data = json.loads(script_tag.string)

        gigs = json_data['listings'][0]['gigs']
        self.insert_gigs(gigs, cursor)
        
        page = json_data['appData']['pagination']['page']
        total = json_data['appData']['pagination']['total']
        category_id = json_data['listings'][0]['gigs'][0]['category_id']
        sub_category_id = json_data['listings'][0]['gigs'][0]['sub_category_id']
        print(f'record_count {len(gigs)} : total {total}')
        if page == 21:
            cursor.execute("""
                UPDATE fiverr_cat_processing
                SET skip = %s
                WHERE id = %s
            """, (False, payload['id']))
        else:
            cursor.execute("""
                    UPDATE fiverr_cat_processing
                    SET category_id = %s, sub_cat_id = %s, page = %s, total = %s
                    WHERE id = %s
                """, (category_id, sub_category_id, page + 1, total, payload['id']))

        return {
                "message": "Success",
                "records_inserted": len(gigs),
                "total_results": total
            }
    
    def insert_gigs(self, gigs, cursor):
        insert_query = """
        INSERT INTO fiverr_gig_web (gigId, pos, is_fiverr_choice, sellerId, impressionId, category_id, sub_category_id, nested_sub_category_id, is_pro, is_featured, cached_slug, title, seller_name, seller_id, seller_country, seller_img, seller_display_name, seller_online, status, offer_consultation, personalized_pricing_fail, has_recurring_option, buying_review_rating_count, buying_review_rating, seller_url, seller_level, gig_url, is_seller_unavailable, price_i, package_i, extra_fast, num_of_packages, u_id, seller_languages, skills, seller_rating_count, seller_rating_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (gigId) DO NOTHING
        """

        for gig in gigs:
            seller_languages = gig.get('seller_languages') or []
            seller_languages_str = ', '.join([f"{lang['code']}:{lang['level']}" for lang in seller_languages])
            metadata = gig.get('metadata', []) or []
            skills = ', '.join([
                ', '.join(skill['value']) if isinstance(skill.get('value'), list) else ''
                for skill in metadata
            ])
            seller_rating_count = gig.get('seller_rating', {}).get('count', 0)
            seller_rating_score = gig.get('seller_rating', {}).get('score', 0)
            
            fields_dict = {
                'gigId': gig.get('gigId'),
                'pos': gig.get('pos', 0),
                'is_fiverr_choice': gig.get('is_fiverr_choice', False),
                'sellerId': gig.get('sellerId'),
                'impressionId': gig.get('impressionId'),
                'category_id': gig.get('category_id'),
                'sub_category_id': gig.get('sub_category_id'),
                'nested_sub_category_id': gig.get('nested_sub_category_id'),
                'is_pro': gig.get('is_pro', False),
                'is_featured': gig.get('is_featured', False),
                'cached_slug': gig.get('cached_slug'),
                'title': gig.get('title'),
                'seller_name': gig.get('seller_name'),
                'seller_id': gig.get('seller_id'),
                'seller_country': gig.get('seller_country'),
                'seller_img': gig.get('seller_img'),
                'seller_display_name': gig.get('seller_display_name'),
                'seller_online': gig.get('seller_online', False),
                'status': gig.get('status'),
                'offer_consultation': gig.get('offer_consultation', False),
                'personalized_pricing_fail': gig.get('personalized_pricing_fail', False),
                'has_recurring_option': gig.get('has_recurring_option', False),
                'buying_review_rating_count': gig.get('buying_review_rating_count', 0),
                'buying_review_rating': gig.get('buying_review_rating', 0.0),
                'seller_url': gig.get('seller_url'),
                'seller_level': gig.get('seller_level', ''),
                'gig_url': gig.get('gig_url'),
                'is_seller_unavailable': gig.get('is_seller_unavailable', False),
                'price_i': gig.get('price_i', 0),
                'package_i': gig.get('package_i', 0),
                'extra_fast': gig.get('extra_fast', False),
                'num_of_packages': gig.get('num_of_packages', 1),
                'u_id': gig.get('u_id'),
                'seller_languages': seller_languages_str,
                'skills': skills,
                'seller_rating_count': seller_rating_count,
                'seller_rating_score': seller_rating_score,
            }

            for field_name, field_value in fields_dict.items():
                if isinstance(field_value, dict):
                    raise ValueError(f"Dictionary detected in field '{field_name}', cannot insert dictionary directly into database. Value: {field_value}")

            cursor.execute(insert_query, tuple(fields_dict.values()))
        cursor.connection.commit()
    
    def get_record_count(self, sub_cat):
        cursor = self.db_connector.cursor
        cursor.execute("SELECT sub_cat_id FROM fiverr_cat_processing WHERE sub_cat_name = %s", (sub_cat,))
        result = cursor.fetchone()
        if result is None:
            return 0
        sub_cat_id = result['sub_cat_id']
        cursor.execute("SELECT COUNT(*) FROM fiverr_gig_web WHERE sub_category_id = %s", (sub_cat_id,))
        return cursor.fetchone()[0]

    def lambda_handler(self, event, context):
        try:
            self.db_connector.connect()
            total_records_inserted = 0

            self.db_connector.cursor.execute("SELECT * FROM fiverr_cat_processing WHERE skip = false ORDER BY RANDOM() LIMIT 5")
            records = self.db_connector.cursor.fetchall()

            for record in records:
                self.sleep_random(5, 30)
                result = self.fetch_and_store_gigs(payload=record)
                total_records_inserted = total_records_inserted + result['records_inserted']

            self.db_connector.connection.commit()
            
            return {
                "message": "Overall Result",
                "total_records_inserted": total_records_inserted,
            }
        except Exception as e:
            print(traceback.format_exc())
            raise e
        finally:
            self.db_connector.disconnect()

# Database connection parameters
db_config = {
    'host': 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com',
    'user': 'postgres',
    'password': 'GWtxSGM4swxxhN3fMHRH',
    'dbname': 'scraper_db'
}

unique_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                            "(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
headers = {
    'authority': 'fiverr.com',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'user-agent': unique_user_agent
}

lambda_handler = LambdaHandler(db_config, headers).lambda_handler
