import json
import boto3
import requests
import psycopg2
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
    # Get SSM Parameters
    ssm = boto3.client('ssm')
    payload_query = ('/upwork-job/12hour-query'
        if has_matches_12hour_trigger
        else '/upwork-job/query'
    )
    print("loading payload %s ...", payload_query)
    ssmPayload = ssm.get_parameter(Name=payload_query, WithDecryption=True)['Parameter']['Value']
    listOfPayload = json.loads(ssmPayload).get('queries')
    # print(listOfPayload)
    # Get OAuth Token from SSM Parameter
    oAuthtokenPayloads = ssm.get_parameter(Name='/upwork-job/oAuthtoken', WithDecryption=True)['Parameter']['Value']
    # print(oAuthtokenPayloads)
    # Get Cookies Token from SSM Parameter
    cookies = ssm.get_parameter(Name='/upwork-job/cookies', WithDecryption=True)['Parameter']['Value']
    # print(cookies)    
    records_inserted = 0
    records_insert_failure = 0
    
    # Check for refresh flag
    # Initialise Loop
    for payload in listOfPayload:
        title = payload.get('title', None)
        query = payload.get('query', '')
        url = "https://www.upwork.com/ab/jobs/search/url?per_page=50&sort=recency%s"%(query)
        headers = {
            "Authorization": "Bearer %s"%(oAuthtokenPayloads),
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.55.3 (Freelancer)",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.upwork.com",
            "Cache-Control": "no-cache",
            "Cookie": cookies
        }
        r = requests.get(url, 
        headers=headers)
        status_code = r.status_code
        
        print(status_code)
        if status_code != 200:
            refreshToken();
            errorMessage = 'Token Expired. Refresh Successful';
            client = boto3.client("ses")
            response = client.send_email(Source = "auto-job-query@marchcroft.com", Destination = {"ToAddresses": ["contactus@marchcroft.com"]}, Message = {"Subject": {"Data": 'Token Refreshed'}, "Body": {"Html": {"Data": errorMessage}}})
            raise Exception(errorMessage)
                        
        jobs = r.json().get('searchResults').get('jobs')
        timeDeltaValue = payload.get('withLastXSeconds', 900)
        recentJobs = []
        for job in jobs:
            format = "%Y-%m-%dT%H:%M:%S%z"
            pubdt = datetime.strptime(job.get('publishedOn'), format).replace(tzinfo=timezone.utc)
            time_threshold = datetime.now(timezone.utc) - timedelta(seconds=timeDeltaValue)
            
            if pubdt > time_threshold:
                recentJobs.append(job)
        records_inserted += len(recentJobs)
        print(recentJobs)
        for job in recentJobs:
            try:
                cursor.execute('''
                    INSERT INTO jobs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                    job['title'], job['createdOn'], job['type'], job['ciphertext'], job['description'], job['category2'],
                    job['subcategory2'], job['duration'], job['shortDuration'], job['durationLabel'], job['engagement'],
                    job['shortEngagement'], job['amount']['currencyCode'], job['amount']['amount'], job['recno'], job['uid'],
                    job['client']['paymentVerificationStatus'], job['client']['location']['country'], job['client']['totalSpent'],
                    job['client']['totalReviews'], job['client']['totalFeedback'], job['client']['companyRid'], job['client']['companyName'],
                    job['client']['edcUserId'], job['client']['lastContractPlatform'], job['client']['lastContractRid'],
                    job['client']['lastContractTitle'], job['client']['feedbackText'], job['client']['companyOrgUid'],
                    job['client']['hasFinancialPrivacy'], job['freelancersToHire'], job['relevanceEncoded'], job['enterpriseJob'],
                    job['tierText'], job['tier'], job['tierLabel'], job['isSaved'], job['feedback'], job['proposalsTier'],
                    job['isApplied'], job['sticky'], job['stickyLabel'], job['jobTs'], job['prefFreelancerLocationMandatory'],
                    json.dumps(job['prefFreelancerLocation']), job['premium'], job['plusBadge'], job['publishedOn'], job['renewedOn'],
                    job['sandsService'], job['sandsSpec'], job['sandsAttrs'], job['occupation'], job['isLocal'], job['workType'],
                    json.dumps(job['locations']), job['weeklyBudget']['currencyCode'], job['weeklyBudget']['amount'],
                    job['hourlyBudgetText'], job['hourlyBudget']['type'], job['hourlyBudget']['min'], job['hourlyBudget']['max'],
                    json.dumps(job['tags']), job['clientRelation'], job['totalFreelancersToHire'], job['teamUid'],
                    job['multipleFreelancersToHirePredicted'], job['connectPrice'], 
                    [label for source in [job["occupations"].get("category", {})] + job["occupations"].get("subcategories", []) + [job["occupations"].get("oservice", {})] for label in [source.get("prefLabel")] if label],
                    [attr.get("prettyName") for attr in job.get("attrs", []) if attr.get("prettyName")]
                ))
                conn.commit()
            except Exception as e:
                records_insert_failure += 1
                print("An error occurred:", e)
                conn.rollback()
                if "duplicate key" in str(e).lower():
                    continue;
                # cursor.execute('''
                #     INSERT INTO failed_job_insert VALUES (%s, %s)
                #     ''', (
                #     job['uid'], json.dumps(job)
                # ))
                # conn.commit()
                # Handle the exception
                client = boto3.client("ses")
                client.send_email(Source = "auto-job-query@marchcroft.com", Destination = {"ToAddresses": ["contactus@marchcroft.com"]}, Message = {"Subject": {"Data": 'Error on insert'}, "Body": {"Html": {"Data": "Error " + str(e) + " "+ json.dumps(job),}}})

    conn.close()

        
    return {
        'statusCode': 200,
        'body': {
            'records_inserted': records_inserted
        }
    }
    
def getCookies():
    ssm = boto3.client('ssm')
    session = requests.Session()
    url = "https://www.upwork.com/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir"
    # print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.55.3 (Freelancer)",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.upwork.com",
        "Cache-Control": "no-cache",
        "Referer": "https://www.upwork.com/en-gb/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir",
        "Origin": "https://www.upwork.com",
        "X-Odesk-Csrf-Token": "8dc920fbc45e70f062aed0e80c23fb16",
        "X-Requested-With": "XMLHttpRequest"
        }
    
    body = {
    	"login": {
    		"mode": "password",
    		"username": "danielsos1017@gmail.com",
    		"rememberme": True,
    		"elapsedTime": 24145,
    		"forterToken": "2f09b55628884328b8f105d5ed24191e_1699371165849__UDF43-m4_14ck_tt",
    		"deviceType": "mobile",
    		"password": "PasswordChange2",
    		"biometricEligible": True
    	}
    }
    try:
        r = session.post(url, 
    headers=headers, json=body)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    cookies = session.cookies.get_dict()
    if cookies:
        ssm.put_parameter(
             Name='/upwork-job/cookies',
             Value= "; ".join([str(x)+"="+str(y) for x,y in cookies.items()]),
             Type='String',
             Overwrite=True
           )
        
def refreshToken():
    ssm = boto3.client('ssm')
    getCookies()
    cookies = ssm.get_parameter(Name='/upwork-job/cookies', WithDecryption=True)['Parameter']['Value']
    print("getCookies(): "+cookies)
    session = requests.Session()
    url = "https://www.upwork.com/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir"
    # print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.55.3 (Freelancer)",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.upwork.com",
        "Cache-Control": "no-cache",
        "Referer": "https://www.upwork.com/en-gb/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir",
        "Origin": "https://www.upwork.com",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": cookies
        }
    
    body = {
        "login": {
            "mode": "password",
            "username": "danielsos1017@gmail.com",
            "rememberme": True,
            "elapsedTime": 24145,
            "forterToken": "2f09b55628884328b8f105d5ed24191e_1699371165849__UDF43-m4_14ck_tt",
            "deviceType": "mobile",
            "password": "PasswordChange2",
            "authToken": "ef8d7afb64c4be78724fe76fe81ab12e4e30477e06917e51c3b078925d548943",
            "securityCheckCertificate": "eyJraWQiOiJyZWdpc3RyYXRpb24ua2V5LnJzYTUxMi5wdWJsaWMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhdXRoRFMiLCJzdWIiOiI4YTE0YjNmOSIsImlzcyI6ImF1dGhEUyIsInZuZF9lb190eXBlIjoiU0VDVVJJVFlfQ0hFQ0siLCJ2ZW5kb3JJZCI6IklPVkFUSU9OIiwiZXhwIjoxNjk5MzcyNjI1LCJpYXQiOjE2OTkzNzI2MTV9.N7RhtgRj6M8DmHB3OGVw7CgHJI8aK-Gf52tDCEQ5nVXpAiY0sklULo8KHpLcAco2r5tF44k3Gxg8GXXLBFkkDg"
        }
    }
    try:
        r = session.post(url, 
    headers=headers, json=body)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)     
    
    oauth_token = session.cookies.get_dict().get('oauth2_global_js_token')
    # cookies = session.cookies.get_dict()
    print("------- Refresh Method")
    print(r.status_code)
    print(r.reason)
    print(oauth_token)
    # print(cookies)
    if oauth_token:
        ssm.put_parameter(
             Name='/upwork-job/oAuthtoken',
             Value=oauth_token,
             Type='String',
             Overwrite=True
           )
    # if cookies:
    #     ssm.put_parameter(
    #          Name='/upwork-job/cookies',
    #          Value= "; ".join([str(x)+"="+str(y) for x,y in cookies.items()]),
    #          Type='String',
    #          Overwrite=True
    #       )

           
