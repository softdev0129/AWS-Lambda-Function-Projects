import json
import boto3
import datetime
from utils.build_response import build_response


class ContactUs:
    def __init__(self, event):
        self.event = event
        self.body = json.loads(event.get("body", {}))
        self.email = self.body.get("email", '')
        self.accountID = self.body.get("account_id", '')
        self.subject = self.body.get("subject", '')
        self.message = self.body.get('message', '')

    def sendEmail(self):
        try:
            time = datetime.datetime.utcnow()
            client = boto3.client("ses")
            body = f"""
                <br>
                This is a notification from marchcroft.com contact us from.
                Contact Us From Received {time} <br>
                Email: {self.email} <br>
                Account ID: {self.accountID} <br>
                Message: {self.message} 
                """
            message = {"Subject": {"Data": self.subject}, "Body": {"Html": {"Data": body}}}
            client.send_email(Source="contactus@marchcroft.com", Destination={"ToAddresses": ["contactus@marchcroft.com"]}, Message=message)
            return build_response(200, {'message': 'Hello from Lambda!'})

        except Exception as e:
            return build_response(400, {'error': str(e)})
