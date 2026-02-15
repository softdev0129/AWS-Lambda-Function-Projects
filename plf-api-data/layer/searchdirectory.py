import urllib

from db.db_manager import DbManager
from db.plf_db_manager import PlfDbManager
from utils.build_response import build_response, build_error_response
from utils.extract_token import extract_token
from firebase_admin import auth


class SearchDirectory:
    def __init__(self, event):
        self.event = event
        self.scraper_db_manager = DbManager()
        self.plf_db_manager = PlfDbManager()

    def fetch_search_directory(self, offset, amount, categories=None, cities=None):
        try:
            search_text = ''
            # Check if any location query is a substring of the cities parameter
            city_list = []
            if cities is not None and cities != 'null':
                for city in cities.split(','):
                    # Parameterize the query to avoid the NoneType issue
                    result = self.scraper_db_manager.fetch_one(
                        "SELECT location_query FROM executions WHERE location_query LIKE %s", (city + '%',))
                    if result is not None and len(result) > 0:  # Ensure result is not None and has at least one element
                        city_list.append(result[0])

            # Format the city list for SQL query
            if city_list:
                # Remove duplicates from city_list
                city_list = list(set(city_list))
                city_filter = "E.location_query IN (" + ','.join([f"'{city}'" for city in city_list]) + ")"
                if search_text:
                    search_text += " AND " + city_filter
                else:
                    search_text = " WHERE " + city_filter

            # Handle category filter using IN clause
            if categories is not None and categories != 'null':
                category_filter = "B.category_name IN (" + ','.join([f"'{cat}'" for cat in categories.split(',')]) + ")"
                if search_text:
                    search_text += " AND " + category_filter
                else:
                    search_text = " WHERE " + category_filter

            # Count total results
            query = """SELECT count(*) FROM contact_details A 
            LEFT JOIN
                results B ON A.result_id = B.id 
            LEFT JOIN
                executions E ON E.id = B.execution_id
                """ + search_text
            print(query)
            total_cnt = self.scraper_db_manager.fetch_all(query)
            total_pages = total_cnt[0][0] // int(amount)
            if total_cnt[0][0] > total_pages * int(amount):
                total_pages += 1
            current_page = int(offset) // int(amount) + 1

            # Fetch search directories from the database
            query = f"""
                SELECT 
                    A.emails, 
                    B.phone, 
                    A.linkedins, 
                    A.instagrams, 
                    A.facebooks, 
                    A.youtubes, 
                    B.title, 
                    B.total_score, 
                    B.reviews_count, 
                    B.website, 
                    B.category_name, 
                    B.url, 
                    A.id,
                    E.search_string AS industry,
                    E.location_query AS city,
                    (COALESCE(array_length(A.emails, 1), 0) +
                     COALESCE(array_length(A.linkedins, 1), 0) + 
                     COALESCE(array_length(A.instagrams, 1), 0) + 
                     COALESCE(array_length(A.facebooks, 1), 0) + 
                     COALESCE(array_length(A.youtubes, 1), 0)) AS social_count,
                    ((CASE WHEN A.linkedins IS NOT NULL AND array_length(A.linkedins, 1) > 0 THEN 1 ELSE 0 END) + 
                     (CASE WHEN A.emails IS NOT NULL AND array_length(A.emails, 1) > 0 THEN 1 ELSE 0 END) + 
                     (CASE WHEN A.instagrams IS NOT NULL AND array_length(A.instagrams, 1) > 0 THEN 1 ELSE 0 END) + 
                     (CASE WHEN A.facebooks IS NOT NULL AND array_length(A.facebooks, 1) > 0 THEN 1 ELSE 0 END) + 
                     (CASE WHEN A.youtubes IS NOT NULL AND array_length(A.youtubes, 1) > 0 THEN 1 ELSE 0 END) +
                     (CASE WHEN B.phone IS NOT NULL THEN 1 ELSE 0 END)) AS has_socials_count
                FROM 
                    contact_details A
                LEFT JOIN 
                    results B ON A.result_id = B.id
                LEFT JOIN 
                    executions E ON E.id = B.execution_id
                {search_text}
                ORDER BY has_socials_count DESC
                LIMIT %s OFFSET %s
            """
            print(query)
            directories = self.scraper_db_manager.fetch_all(query, (amount, offset))
            self.scraper_db_manager.close()

            # Format the response
            search_directories = []
            for directory in directories:
                search_directories.append({
                    'hasEmail': directory[0] != [],
                    'emailCount': len(directory[0]),
                    'hasPhone': directory[1] != [],
                    'hasLinkedin': directory[2] != [],
                    'linkedInCount': len(directory[2]),
                    'hasInstagram': directory[3] != [],
                    'instagramCount': len(directory[3]),
                    'hasFacebook': directory[4] != [],
                    'facebookCount': len(directory[4]),
                    'hasYoutube': directory[5] != [],
                    'youtubeCount': len(directory[5]),
                    'title': directory[6],
                    'total_score': directory[7],
                    'reviews_count': directory[8],
                    'website': directory[9] != [],
                    'category_name': directory[10],
                    'url': directory[11] != [],
                    'id': directory[12],
                    'industry': directory[13],  # Add industry
                    'city': directory[14]  # Add city
                })
            return build_response(200, {'search_directories': search_directories, 'total_cnt': total_cnt[0][0],
                                        'total_pages': total_pages, 'current_page': current_page})
        except Exception as e:
            return build_error_response(400, {'error': str(e)})

    def fetch_contact_info(self, id):
        try:
            id_token = extract_token(self.event)
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            query = "SELECT B.amount FROM billing_credit B LEFT JOIN users U ON B.id = U.billing_credit_id WHERE U.uid=%s"
            credit_amount_data = self.plf_db_manager.fetch_one(query, (uid,))
            if credit_amount_data[0] < 2:
                return build_response(400, {'error': 'There is not enough credit amount.'})

            query = "UPDATE billing_credit SET amount = amount - 2 WHERE id = (SELECT billing_credit_id FROM users WHERE uid=%s)"
            self.plf_db_manager.execute_query(query, (uid,))

            # Fetch contact details from the database
            query = "SELECT A.emails, B.phone, A.linkedins, A.instagrams, A.facebooks, A.youtubes FROM contact_details A LEFT JOIN results B ON A.result_id = B.id WHERE A.id = %s"
            contact = self.plf_db_manager.fetch_one(query, (id,))
            self.plf_db_manager.close()

            contact_info = {
                'emails': contact[0],
                'phones': contact[1],
                'linkedins': contact[2],
                'instagrams': contact[3],
                'facebooks': contact[4],
                'youtubes': contact[5],
            }
            # Format the response
            return build_response(200, {'contact_info': contact_info})
        except Exception as e:
            return build_error_response(400, {'error': str(e)})
