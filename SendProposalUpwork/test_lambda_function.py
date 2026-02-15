from job_description_test_data import sample_text
from proposal_generator import get_proposal
from upwork_helper import get_job_details, post_job_proposal, post_project_proposal, AuthTokenFailedException
from auth import refresh_token
import boto3
import random
import time

# import json
# from datetime import datetime, timedelta, timezone
# import pytz

db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'
db_name_transaction = 'scraper_db'


# Function to sleep for a random duration
def test_ai_response():
    generated_proposal = get_proposal(sample_text).replace("[Your Name]", "David")
    # generated_proposal = "I can do the Job for you"
    print(generated_proposal)

def test_proposal_post():
    records_inserted = 0
    records_insert_failure = 0

    # collect jobs to apply for here
    query = """
    SELECT *
    FROM jobs
    WHERE LOWER(skills) LIKE '%react%'
    AND (hourlybudget_max > 35 OR amount_amount > 1000)
    AND client_totalspent > 3000
    AND client_totalfeedback > 4.8
    AND (preffreelancerlocationmandatory = FALSE OR (preffreelancerlocationmandatory = TRUE AND LOWER(preffreelancerlocation) LIKE LOWER('%United%Kingdom%')))
    AND publishedon >= CURRENT_TIMESTAMP - INTERVAL '1440 minutes';
    """

    # query = """
    # SELECT *
    # FROM jobs
    # ORDER BY createdon DESC
    # LIMIT 1
    # """

    # Execute the SQL query

    # Fetch the results

    # Generate job proposal
    generated_proposal = "I can help you here"
    # generated_proposal = "I can do the Job for you"
    print(generated_proposal)

    try:
        job_details = get_job_details("~01999990e40b59f579")
        post_job_proposal(job_details, generated_proposal)
        insert_query = """
                    INSERT INTO public.upwork_job_proposals (job_id, proposal, createdon)
                    VALUES (%s, %s, %s);
                """

    except AuthTokenFailedException as e:
        refresh_token()
        error_message = 'Token Expired. Refresh Successful'
        client = boto3.client("ses")
        client.send_email(Source="auto-job-query@marchcroft.com",
                              Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                              Message={"Subject": {"Data": 'Access Error in Send Proposal - Token Refresh'},
                                       "Body": {"Html": {"Data": error_message}}})
        raise e
    except Exception as e:
        error_message = str(e)
        client = boto3.client("ses")
        client.send_email(Source="auto-job-query@marchcroft.com",
                                     Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                                     Message={"Subject": {"Data": 'Error in Send Proposal'},
                                                  "Body": {"Html": {"Data": error_message}}})
        raise e

    return {
        'statusCode': 200,
        'body': {
            'Message': 'Processed job successfully'
        }
    }
