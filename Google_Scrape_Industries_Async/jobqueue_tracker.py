import boto3
import json
from datetime import datetime
from event_action import EventAction  # Ensure the correct import

client = boto3.client('lambda')

def start_job_event(event_name):
    payload = {
        'action': EventAction.START_JOB.value,
        'event_name': event_name,
    }
    response = invoke_lambda(payload)
    job_id = response.get('id')  # Capture the job ID returned from the start job event
    if job_id:
        print(f"Started job with ID: {job_id}")
    return job_id

def complete_job_event(job_id):
    payload = {
        'action': EventAction.COMPLETE_JOB.value,
        'id': job_id,
    }
    invoke_lambda(payload)

def fail_job_event(job_id):
    payload = {
        'action': EventAction.FAIL_JOB.value,
        'id': job_id,
    }
    invoke_lambda(payload)

def invoke_lambda(payload):
    try:
        response = client.invoke(
            FunctionName='Job_Queue_Site',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        
        if response_payload.get('statusCode') != 200:
            print(f"Invocation of {payload['action']} for {payload.get('event_name', payload.get('id'))} failed with response: {response_payload}")
        else:
            print(f"Invocation of {payload['action']} for {payload.get('event_name', payload.get('id'))} succeeded with response: {response_payload}")
        
        return response_payload.get('body') and json.loads(response_payload.get('body'))

    except Exception as e:
        print(f"Error invoking Lambda function: {str(e)}")
        return None

