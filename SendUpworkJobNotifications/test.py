import json
import requests
import psycopg2
import time
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta, timezone

# import pytz

db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'
db_name_transaction = 'scraper_db'


def lambda_handler(event, context):
    # event = event.get('resources')

    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name_transaction)
    cursor = conn.cursor(cursor_factory=DictCursor)

    resources = event.get('resources', [])
    has_matches_12hour_trigger = any("12hour_Trigger" in resource for resource in resources)
    records_inserted = 0
    records_insert_failure = 0
    oAuthtokenPayloads = 'oauth2v2_17a0958b07659e3c9f2972a50e2ea2b5'
    cookies = 'SZ=497b7822d99b266dd5d4b7fe684981c3f964f4e422f3f04afd1a9c0e5c0be02e; __cf_bm=aLM1DWQeM3a.Tuqo2Qcf.lXth1GWUVGNrLK5H1MV.PY-1707026634-1-Af7tRirq/wux0m01vzaT97FyweoH+VDP3Ezv11a3iZ2MLZco2TmUNQZ/6bNERVCcj//5v5BDDTU27dLNbXjGzTc=; _cfuvid=EULwAljMgya4DC9P9WICqhmrNlWvCVXLkYpgU6jeNkk-1707026634393-0-604800000; company_last_accessed=d1046535580; console_user=8a14b3f9; current_organization_uid=1721871863404507137; master_access_token=ef238cb0.oauth2v2_54fb66b7de38e67938e6c451239a9c5c; oauth2_global_js_token=oauth2v2_768dba30324814a6851ec811a4eba6fc; recognized=8a14b3f9; user_uid=1721871863404507136; visitor_id=3.249.91.173.1707026633447000; master_refresh_token=ef238cb0.oauth2v2_e498fae09976df9754ffe5ded6d5733a.1; __cflb=02DiuEXPXZVk436fJfSVuuwDqLqkhavJbS6Qh4G4oWz3d; cookie_domain=.upwork.com; cookie_prefix=; enabled_ff=CLOBJNAIR3,!CLOBJPGV2RJP,!MP16400Air3Migration,!i18nGA,TONB2256Air3Migration,JPAir3,i18nOn,FLSAir3,!RMTAir3Talent,CI9570Air2Dot5,SSINavUserBpa,!CI10857Air3Dot0,!air2Dot76Qt,CI11132Air2Dot75,air2Dot76,OTBnrOn,!CI10270Air2Dot5QTAllocations,!CI12577UniversalSearch,!RMTAir3Hired,!RMTAir3Home,CLOBSNAIR3,!SSINavUser'

    query = "SELECT ciphertext FROM jobs where occupations is null"
    cursor.execute(query)
    result = cursor.fetchall()

    # Extracting 'ciphertext' values from the result
    ciphertext_list = [row[0] for row in result]

    # Check for refresh flag
    # Initialise Loop
    for jobId in ciphertext_list:
        url = "https://www.upwork.com/job-details/jobdetails/api/job/%s/details" % (jobId)
        headers = {
            "Authorization": "Bearer %s" % (oAuthtokenPayloads),
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.55.3 (Freelancer)",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.upwork.com",
            "Cache-Control": "no-cache",
            "Cookie": cookies
        }
        r = requests.get(url,
                         headers=headers)
        status_code = r.status_code

        job = r.json()
        try:
            print(job)
            occupations = None
            skills = []

            if 'sands' in job:
                if 'occupation' in job['sands'] and 'prefLabel' in job['sands']['occupation']:
                    occupations = job['sands']['occupation']['prefLabel']

                if 'additionalSkills' in job['sands']:
                    skills = [skill['name'] for skill in job['sands']['additionalSkills'] if 'name' in skill]

            # Update the database only if occupations and/or skills have values
            if occupations or skills:
                cursor.execute('''UPDATE jobs
                SET occupations = %s, skills = %s
                WHERE ciphertext = %s''', (occupations, skills, jobId))
                conn.commit()
                records_inserted += 1
            else:
                print(f"No update for job ID {jobId} due to empty occupations and skills.")
        except Exception as e:
            records_insert_failure += 1
            print("An error occurred:", e)

        time.sleep(0.5)
    conn.close()

    return {
        'statusCode': 200,
        'body': {
            'records_updated': records_inserted,
            'records_failed': records_insert_failure
        }
    }
