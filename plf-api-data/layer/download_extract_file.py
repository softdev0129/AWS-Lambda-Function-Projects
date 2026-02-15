import csv
import logging
import traceback
import json
import base64
from io import StringIO, BytesIO

from db.db_manager import DbManager
from db.plf_db_manager import PlfDbManager

# Configure logging
logging.basicConfig(level=logging.INFO)


def fetch_and_produce_csv(id, file_type):
    db_manager = PlfDbManager()
    scraper_db_manager = DbManager()
    try:
        # Establish connection to the database
        logging.info("Connecting to the database...")
        # Fetch record from international_weekly_extract using id
        logging.info(f"Fetching record for id {id}...")
        query = """
            SELECT industry, to_char(extract_time, 'DD-MM-YYYY') AS formatted_extract_time, json_result
            FROM international_extract
            WHERE id = %s
        """
        row = db_manager.fetch_one(query, (id,))

        if not row:
            error_msg = f"No record found for id {id}"
            logging.error(error_msg)
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": error_msg})
            }

        industry = row[0]
        extract_time = row[1]
        json_result = row[2]  # Assuming json_result is already a JSON string

        # Extract g_contact_details ids from json_result (assuming json_result is already a JSON string)
        ids = json_result.get("g_contact_details", [])
        if not ids:
            error_msg = "No g_contact_details found in json_result"
            logging.error(error_msg)
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": error_msg})
            }

        # Prepare comma-separated string of ids for SQL query
        ids_str = ','.join(map(str, ids))

        # Fetch email from contact_details using extract_type and ids
        logging.info(f"Fetching emails for ids: {ids_str}...")
        query_contact_details = f"""
            SELECT c.emails
            FROM results r
            JOIN contact_details c ON r.id = c.result_id
            WHERE r.id IN ({ids_str})
            AND c.emails IS NOT NULL
        """
        contact_details_rows = scraper_db_manager.fetch_all(query_contact_details)

        # Prepare CSV file content based on fetched data
        csv_data = []
        for contact_row in contact_details_rows:
            emails_list = contact_row[0] if contact_row[0] else []
            if emails_list:
                for email in emails_list:
                    csv_data.append({"email": email.strip()})  # Add each email as a new row

        if not csv_data:
            error_msg = "No valid emails found for the given ids"
            logging.error(error_msg)
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": error_msg})
            }

        # Generate CSV in-memory using StringIO
        # csv_buffer = StringIO()
        # csv_writer = csv.DictWriter(csv_buffer, fieldnames=["email"])
        # csv_writer.writeheader()  # Write header row
        # csv_writer.writerows(csv_data)
        #
        # # Get CSV content from buffer as bytes
        # csv_content_bytes = csv_buffer.getvalue().encode('utf-8')
        plain_text_content = ", ".join([f"{{\"email\" : \"{data['email']}\"}}" for data in csv_data])
        plain_text_content = "[" + plain_text_content + "]"
        db_manager.close()
        # Return success response with CSV content as bytes
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                "Content-Type": "text/plain",
                'Content-Disposition': 'inline'
            },
            "body": plain_text_content
        }
    except Exception as e:
        # Log detailed traceback information
        logging.error("An error occurred:")
        logging.error(traceback.format_exc())

        db_manager.close()

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }


if __name__ == "__main__":
    # Simulate invoking the function with parameters (1, "csv")
    result = fetch_and_produce_csv(1, "csv")

    # Print the result for testing purposes
    print(result)
