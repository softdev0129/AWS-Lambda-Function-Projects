import json
import firebase_admin
from firebase_admin import credentials
import os

from cloudwatch.cloud_watch import CloudWatchLogFetcher
from layer.data_layer import DataLayer
from event_type_enum import EventType
from layer.download_extract_file import fetch_and_produce_csv
from layer.get_extract_files import get_extract_file
from layer.get_more_files import get_more_file
from layer.get_local_leads import LocalLeads
from layer.search_leads import SearchLeads
from layer.get_companies import fetch_companies
from layer.searchdirectory import SearchDirectory

firebase_cred = os.environ['FIREBASE_CREDENTIALS']
print(f'FIREBASE CRED - {firebase_cred}')
# Initialize Firebase Admin SDK
print(os.environ['FIREBASE_CREDENTIALS'].replace("\\n", "\n"))
cred = credentials.Certificate(json.loads(os.environ['FIREBASE_CREDENTIALS']))
firebase_admin.initialize_app(cred)

log_fetcher = CloudWatchLogFetcher()


def fetch_html():
    with open('index.html', 'r') as file:
        return file.read()


def lambda_handler(event, context):
    path = event.get('path')
    event_type = EventType.from_path(path)

    if event_type == 'DATA_DOWNLOAD':
        body = json.loads(event.get('body', {}))
        extract_id = body.get('id', None)
        file_type = body.get('file_type', None)
        if extract_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid id is missing')
            }
        if file_type is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid file_type is missing')
            }
        return fetch_and_produce_csv(extract_id, file_type)
    elif event_type == 'GET_MORE_CATEGORIES':
        query_params = event.get('queryStringParameters', {})
        industry = query_params.get('industry', None)

        if industry is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid industry is missing')
            }
        return get_more_file(industry)
    elif event_type == 'SEARCH_DIRECTORY':
        query_params = event.get('queryStringParameters', {})
        handler = SearchDirectory(event)
        response = handler.fetch_search_directory(query_params.get('offset', 0), query_params.get('amount', 10), query_params.get('category_name', None), query_params.get('city', None))
    elif event_type == 'GET_CONTACT_INFO':
        query_params = event.get('queryStringParameters', {})
        handler = SearchDirectory(event)
        response = handler.fetch_contact_info(query_params.get('id', None))
    elif event_type == 'GET_INTERNATIONAL_CATEGORIES':
        return get_extract_file()
    elif event_type == 'GET_LOCAL_CATEGORIES':
        query_params = event.get('queryStringParameters', {})
        handler = LocalLeads()
        response = handler.get_local_leads(query_params.get('location', None))
    elif event_type == 'SEARCH_CATEGORIES':
        query_params = event.get('queryStringParameters', {})
        handler = SearchLeads()
        response = handler.search_leads(query_params.get('keyword', None))
    elif event_type == 'GET_COMPANIES':
        response = fetch_companies()
    elif event_type == 'GET_INTERNATION_EMAIL':
        handler = DataLayer(event)
        response = handler.get_internation_email()
    elif event_type == 'GET_INTERNATION_NUMBER':
        handler = DataLayer(event)
        response = handler.get_internation_number()
    elif event_type == 'GET_LOCALE_EMAIL':
        handler = DataLayer(event)
        response = handler.get_locale_email()
    elif event_type == 'GET_LOCALE_NUMBER':
        handler = DataLayer(event)
        response = handler.get_locale_number()
    elif event_type == 'GET_SERVICED_LINKS':
        handler = DataLayer(event)
        response = handler.get_serviced_links()
    elif event_type == 'FETCH_LOGS':
        query_params = event.get('queryStringParameters', {})
        log_group_name = query_params.get('logGroupName', None)
        if log_group_name:
            log_stream_name = log_fetcher.get_log_streams(log_group_name)
            if log_stream_name:
                log_messages = log_fetcher.get_log_events(log_group_name, log_stream_name)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps(log_messages)
                }
    elif event_type == 'GET_HTML':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
            },
            'body': fetch_html()
        }
    else:
        print(f'DB Used {os.environ["RDS_PLF_DB_NAME"]}')
        response = {
            'statusCode': 400,
            'body': json.dumps('Invalid event type')
        }

    return response
