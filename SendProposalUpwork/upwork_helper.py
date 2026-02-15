import requests
from string import Template
import json
import boto3
import logging
from templates import hp_template, pp_template

ssm = boto3.client('ssm')

# Type 1 = Projects // Type 2 = Hourly Job
def post_job_proposal(job_details, cover_letter):
    job_type = job_details.get('job', {}).get('type', 0)
    if job_type == 1:
        return post_project_proposal(job_details, cover_letter)
    elif job_type == 2:
        return post_hourly_proposal(job_details, cover_letter)
    raise Exception(f"Job Type error {job_type}")

def post_project_proposal(job_details, cover_letter):
    template = pp_template
    dict = {
        "jobReference": job_details.get('job', {}).get('uid'),
        "chargedAmount": job_details.get('job', {}).get('budget', {}).get('amount'),
        "coverLetter": cover_letter,
    }
    template.update(dict)

    if template is not None:
        url = "https://www.upwork.com/ab/proposals/api/v2/application/new"
        return upwork_request(url, method='POST', data=template)
    raise

def post_hourly_proposal(job_details, cover_letter):
    template = hp_template
    amount = job_details.get('job', {}).get('extendedBudgetInfo', {}).get('hourlyBudgetMax')
    dict = {
        "jobReference": job_details.get('job', {}).get('uid'),
        "chargedAmount": 80 if amount > 80 else amount,
        "coverLetter": cover_letter,
    }
    template.update(dict)

    if template is not None:
        url = "https://www.upwork.com/ab/proposals/api/v2/application/new"
        return upwork_request(url, method='POST', data=template)
    raise

def get_job_details(job_id):
    print(f"JOB_ID==={job_id}")
    url = "https://www.upwork.com/job-details/jobdetails/api/job/%s/summary" % (job_id)
    job_details = upwork_request(url, method='GET')
    questions = job_details.get("job", {}).get("questions", [])
    if len(questions) > 0:
        raise Exception(f"Found {len(questions)} questions I cannot handle currently ")
    return job_details

def upwork_request(url, method, data={}):
    print(f"URL REQUEST:{url}")
    oAuthtokenPayloads = ssm.get_parameter(Name='/upwork-job/proposal/oAuthtoken', WithDecryption=True)['Parameter'][
        'Value']
    cookies = ssm.get_parameter(Name='/upwork-job/proposal/cookies', WithDecryption=True)['Parameter']['Value']
    cookies = cookies + ';XSRF-TOKEN=5d3d1303de92b2dd829a48bfbabf666f;'
    print(f"METHOD:{method}")
    headers = {
        "Authorization": "Bearer %s" % oAuthtokenPayloads,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.60.3 (Freelancer)",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.upwork.com",
        "Cache-Control": "no-cache",
        "Cookie": cookies,
        "X-Odesk-Csrf-Token": "5d3d1303de92b2dd829a48bfbabf666f",
        "Origin": "https://www.upwork.com"
    }
    if data:
        body_str = json.dumps(data)
        content_length = len(body_str.encode('utf-8'))
        updated_headers = {
            "Content-Length": str(content_length)
        }
        headers.update(updated_headers)
    print(f"HEADERS:{headers}")
    if method == 'GET':
        r = requests.get(url,
                         headers=headers)
    elif method == 'POST':
        r = requests.post(url, json=data,
                         headers=headers)
    status_code = r.status_code
    print(f"Status Code - {status_code}")
    print(f"Response Body - {r.json()}")
    if status_code == 401:
        raise AuthTokenFailedException(f"Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    if status_code == 403:
        raise Exception(f"Opps Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    if status_code == 400:
        print(r.json())
        raise Exception(f"Opps Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    if status_code != 200:
        raise Exception(f"Opps Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    return r.json()

class AuthTokenFailedException(Exception):
    pass

