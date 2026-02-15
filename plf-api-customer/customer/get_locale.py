import requests
from utils.build_response import build_response, build_error_response
import traceback

import requests


def get_location_info_details(lat, lon):
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'MyApp/1.0 (myemail@example.com)'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        result = response.json()

        if not result:
            print("No results found for the address.")
            return None, None

        # Extract city and country from the result
        city = result.get('address', {}).get('city', None)
        country = result.get('address', {}).get('country', None)

        return city, country

    except requests.exceptions.HTTPError as http_err:
        traceback.print_exc()
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        traceback.print_exc()
        print("Error connecting to the Nominatim service.")
    except requests.exceptions.Timeout:
        traceback.print_exc()
        print("The request to the Nominatim service timed out.")
    except requests.exceptions.RequestException as req_err:
        traceback.print_exc()
        print(f"Error occurred: {req_err}")
    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred: {str(e)}")

    return None, None


def get_location_info(ip_address):
    try:
        url = f'https://ipapi.co/{ip_address}/json/'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            city, country = get_location_info_details(data.get('latitude', None), data.get('longitude', None))
            location = {
                'capital': data.get('country_capital', ''),
                'city': data.get('city', ''),
                'city2': city,
                'region': data.get('region', ''),
                'country': data.get('country_name', ''),
                'loc': f"{data.get('latitude', '')},{data.get('longitude', '')}",
                'languages': data.get('languages', ''),
                'currency': data.get('currency', ''),
            }
            return build_response(200, location)
        else:
            return build_error_response(response.status_code, {'error': 'Failed to retrieve location information'})
    except Exception as e:
        return build_error_response(400, {'error': str(e)})
