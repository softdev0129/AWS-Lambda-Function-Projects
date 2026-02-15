import boto3

class CloudWatchLogFetcher:
    def __init__(self):
        self.client = boto3.client('logs')

    def get_log_streams(self, log_group_name):
        streams = self.client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        if streams['logStreams']:
            return streams['logStreams'][0]['logStreamName']
        return None

    def get_log_events(self, log_group_name, log_stream_name):
        response = self.client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startFromHead=False
        )
        events = response['events']
        log_messages = [event['message'] for event in events]
        return log_messages
