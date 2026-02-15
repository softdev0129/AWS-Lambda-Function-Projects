import json
import os
import boto3
from firebase_admin import auth
from utils.build_response import build_response


class ResetPassword:
    def __init__(self, event):
        self.body = json.loads(event['body'])
        self.email = self.body['email']
        self.from_email = os.environ['FROM_EMAIL']

        # AWS credentials
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

        # Initialize AWS SES client with credentials
        self.ses_client = boto3.client('ses',
                                       region_name='eu-west-1',  # Replace with your AWS region
                                       aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key)

    def send_reset_email(self):
        try:
            # Generate a password reset link
            reset_link = auth.generate_password_reset_link(self.email)

            # Create the email content
            email_subject = 'Password Reset Request'
            email_body = f'Please click the following link to reset your password: <a href="{reset_link}">{reset_link}</a>'
            charset = 'UTF-8'

            # Send email via AWS SES
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [self.email]},
                Message={
                    'Subject': {'Data': email_subject, 'Charset': charset},
                    'Body': {'Html': {'Data': email_body, 'Charset': charset}}
                }
            )

            return build_response(response['ResponseMetadata']['HTTPStatusCode'], 'Password reset email sent successfully!')

        except Exception as e:
            return build_response(400, {'error': str(e)})
