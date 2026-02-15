import json
import re
import traceback

import psycopg2
from psycopg2.extras import DictCursor
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
def sleep_random(min_duration, max_duration):
    sleep_duration = random.uniform(min_duration, max_duration)
    time.sleep(sleep_duration)


def lambda_handler(event, context):
    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name_transaction)
    cursor = conn.cursor(cursor_factory=DictCursor)
    client = boto3.client("ses")
    job_id = event.get("job_id", None)

    records_inserted = 0
    records_insert_failure = 0

    # collect jobs to apply for here
    if job_id:
        return process_job_with_job_id(job_id)

    # Fetch skills from the database
    skills = fetch_skills()
    query = create_dynamic_sql(skills)
    print(f"SQL query==={query}")

    # query = """
    # SELECT *
    # FROM jobs
    # ORDER BY createdon DESC
    # LIMIT 1
    # """

    # Execute the SQL query
    cursor.execute(query)

    # Fetch the results
    job = cursor.fetchone()
    return process_job_proposal(job)


def fetch_skills():
    # Establish a connection to the database
    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name_transaction)
    cursor = conn.cursor(cursor_factory=DictCursor)

    # SQL to fetch skills
    cursor.execute("SELECT DISTINCT skill_name FROM skills_table")
    skills = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return skills
def process_job_with_job_id(job_id):
    job_details = get_job_details(job_id)
    process_job(job_details.get("job").get("ciphertext"),
                job_details.get("job").get("description"),
                job_details.get("job").get("title"))


def process_job_proposal(job):
    if job == None:
        print("None to process")
        return {
            'statusCode': 200,
            'body': {
                'Message': "None to process"
            }
        }
    process_job(job['ciphertext'], job['description'], job['title'])


def create_dynamic_sql(skills, min_hourly_budget=35, min_amount=1000, min_total_spent=0, location="United Kingdom",
                       recent_minutes=10):
    import psycopg2  # You'll need psycopg2 or another database adapter to execute this SQL

    # Start with the base part of the query
    sql = """
    SELECT *
    FROM jobs
    WHERE ("""

    # Dynamically add LIKE conditions for skills
    like_clauses = [f"LOWER(skills) LIKE '%{skill.lower()}%'" for skill in skills]
    sql += " OR ".join(like_clauses)

    # Add other conditions
    sql += f") AND (hourlybudget_max > {min_hourly_budget} OR amount_amount > {min_amount})"
    sql += f" AND client_totalspent > {min_total_spent}"
    sql += f" AND (preffreelancerlocationmandatory = FALSE OR (preffreelancerlocationmandatory = TRUE AND LOWER(preffreelancerlocation) LIKE LOWER('%{location}%')))"
    sql += f" AND publishedon >= CURRENT_TIMESTAMP - INTERVAL '{recent_minutes} minutes'"
    sql += " ORDER BY RANDOM()"
    sql += " LIMIT 1;"

    return sql
def process_job(job_id, description, title):
    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name_transaction)
    cursor = conn.cursor(cursor_factory=DictCursor)
    client = boto3.client("ses")
    # Generate job proposal
    generated_proposal = (get_proposal(description)
                          .replace("[Your Name]", "David")
                          .replace("[Client's Name]", "Hiring Manager")
                          .replace("[X years]", "11+")
                          .replace("[X years/months]", "11+")
                          .replace("[INSERT ESTIMATED COST]", "TBC")
                          .replace("[Number of years]", "11+")
                          .replace("[Your Team Name]", "David - Marchcroft Digital"))

    # Replace the matched text with the desired replacement text
    generated_proposal = re.sub(r'\[.*?]', '', generated_proposal)
    # generated_proposal = "I can do the Job for you"
    print(generated_proposal)

    try:
        generated_proposal_lower = generated_proposal.lower()
        if "upwork" in generated_proposal_lower or "profile_data.txt" in generated_proposal_lower or re.search(
                r"\[.*?\]", generated_proposal_lower):
            insert_query = """
                                    INSERT INTO public.upwork_job_proposals (job_id, proposal, createdon, complete)
                                    VALUES (%s, %s, %s, %s);
                                """
            cursor.execute(insert_query, (job_id, generated_proposal, None, False))
            conn.commit()
            raise Exception(f"Dodgy proposal contains try again {job_id}")
        job_details = get_job_details(job_id)
        post_job_proposal(job_details, generated_proposal)
        insert_query = """
                        INSERT INTO public.upwork_job_proposals (job_id, proposal, createdon, complete)
                        VALUES (%s, %s, %s, %s);
                    """
        cursor.execute(insert_query, (job_id, generated_proposal, job_details.get('publishedon'), True))
        conn.commit()

    except AuthTokenFailedException as e:
        print(traceback.format_exc())
        refresh_token()
        error_message = 'Token Expired. Refresh Successful'
        client.send_email(Source="auto-job-query@marchcroft.com",
                          Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                          Message={"Subject": {"Data": 'Access Error in Send Proposal - Token Refresh'},
                                   "Body": {"Html": {"Data": error_message}}})
        raise e
    except Exception as e:
        print(traceback.format_exc())
        error_message = str(e)
        client.send_email(Source="auto-job-query@marchcroft.com",
                          Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                          Message={"Subject": {"Data": 'Error in Send Proposal'},
                                   "Body": {"Html": {"Data": error_message}}})
        raise e

    conn.close()

    client.send_email(Source="auto-job-query@marchcroft.com",
                      Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                      Message={"Subject": {"Data": 'Successfully Submitted Job'},
                               "Body": {"Html": {
                                   "Data": f"JOB ID==={job_id}===TITLE==={title}==="}}})

    return {
        'statusCode': 200,
        'body': {
            'Message': 'Processed job successfully'
        }
    }
