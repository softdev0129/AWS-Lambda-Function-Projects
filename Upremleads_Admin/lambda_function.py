import json
import os
import pg8000
from urllib.parse import unquote
import base64
import mimetypes
from datetime import datetime

# Database settings
rds_host = "database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com"
name = "postgres"
password = "GWtxSGM4swxxhN3fMHRH"
db_name = "scraper_db"

# Connection
def get_connection():
    return pg8000.connect(host=rds_host, user=name, password=password, database=db_name)

def lambda_handler(event, context):
    path = event.get('path', '/')
    print(context)
    print(event)
    print(f"===PATH {path}")
    http_method = event.get('httpMethod', None)

    if http_method == 'GET' and '/api' in path:
        return get_data(event.get('queryStringParameters') or {})
    elif http_method == 'POST' and '/api' in path:
        return update_data(event['body'])
    else:
        return serve_static_file(path)

def dict_cursor(cursor):
    "Convert the cursor output to dictionaries"
    columns = [desc[0] for desc in cursor.description]
    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))
        for key, value in row_dict.items():
            if isinstance(value, datetime):
                row_dict[key] = value.isoformat()
        yield row_dict

def get_data(params):
    print(f"params {params}")
    connection = get_connection()
    page = int(params.get('page', 1))
    limit = int(params.get('limit', 10))
    show_duplicates = int(params.get('showDuplicates', 0))
    offset = (page - 1) * limit

    print(f"showDuplicates = {show_duplicates}")
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    fiverr_image_links.id AS fiverr_image_link_id, 
                    fiverr_image_links.*, 
                    j.*
                FROM fiverr_image_links 
                LEFT JOIN linkedin_links j 
                ON fiverr_image_links.id = j.image_link_id 
                WHERE fiverr_image_links.linkedin IS NOT NULL
            """
            if show_duplicates != 1:
                sql = sql + " AND fiverr_image_links.is_duplicate = false"
            sql = sql + " ORDER BY fiverr_image_links.id ASC LIMIT %s OFFSET %s" 
            print(sql%(limit,offset))
            cursor.execute(sql, (limit, offset))
            result = list(dict_cursor(cursor))
            cursor.execute("SELECT COUNT(*) FROM fiverr_image_links WHERE linkedin IS NOT NULL AND is_duplicate = false")
            total_rows = cursor.fetchone()[0]
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'data': result,
                    'total': total_rows,
                    'page': page,
                    'limit': limit
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  # Allow all origins
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',  # Allowed methods
                    'Access-Control-Allow-Headers': 'Content-Type'  # Allowed headers
                }
            }
    finally:
        connection.close()

def update_data(body):
    connection = get_connection()
    print(body)
    try:
        data = json.loads(body)
        if not isinstance(data, list):
            raise ValueError("Data should be a list of updates")

        with connection.cursor() as cursor:
            for item in data:
                id = int(item['id'])  # Ensure id is an integer
                column_name = item['columnName']
                new_value = item['newValue']

                # Ensure column name is a valid string and escape dangerous characters
                if not column_name.isidentifier():
                    print(f"Invalid column name {column_name}")
                    raise ValueError("Invalid column name")

                # Check if the id exists in the image_link_id column
                cursor.execute("SELECT 1 FROM linkedin_links WHERE image_link_id = %s", (id,))
                exists = cursor.fetchone()
                if column_name == 'is_duplicate':
                    print(f"is_duplicate update")
                    # Update existing entry
                    sql = f"UPDATE fiverr_image_links SET {column_name} = %s WHERE id = %s"
                    cursor.execute(sql, (new_value, id))
                elif exists:
                    print(f"Entry exists")
                    # Update existing entry
                    sql = f"UPDATE linkedin_links SET {column_name} = %s WHERE image_link_id = %s"
                    cursor.execute(sql, (new_value, id))
                else:
                    print(f"Entry does not exist, creating new")
                    # Insert new entry
                    sql = f"INSERT INTO linkedin_links (image_link_id, {column_name}) VALUES (%s, %s)"
                    cursor.execute(sql, (id, new_value))

            connection.commit()
            return {
                'statusCode': 200,
                'body': json.dumps('Batch update successful'),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  # Allow all origins
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',  # Allowed methods
                    'Access-Control-Allow-Headers': 'Content-Type'  # Allowed headers
                }
            }
    except ValueError as ve:
        print(ve)
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error: {ve}')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
    finally:
        connection.close()


def serve_static_file(path):
    path = path.replace('/prod', '') 
    if path == '/':
        path = '/index.html'

    file_path = './build' + unquote(path)
    
    if not os.path.isfile(file_path):
        return {
            'statusCode': 404,
            'body': 'File not found'
        }
    
    with open(file_path, 'rb') as file:
        content = file.read()
    
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
        
    is_binary = not content_type.startswith('text/')
    body = content if is_binary else content.decode('utf-8')
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': content_type
        },
        'body': body,
        'isBase64Encoded': is_binary
    }
