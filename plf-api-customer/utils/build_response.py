import json
import traceback
from decimal import Decimal


def build_error_response(status_code, error_message):
    # Capture the traceback information as a string
    tb_str = traceback.format_exc()

    # Print traceback to the console or log
    traceback.print_exc()
    return build_response(status_code, {'error': error_message, 'traceback': tb_str})


def build_response(status_code, message):
    if type(message) is str:
        message = {'message': message}

    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(message, default=decimal_default)
    }
