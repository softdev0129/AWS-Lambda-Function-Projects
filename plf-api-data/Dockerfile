# Use the Amazon Linux 2 image provided by AWS Lambda
FROM public.ecr.aws/lambda/python:3.8

# Install system packages
RUN yum install -y gcc python38-devel

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy the Lambda function code
COPY . .

# Command to run the Lambda function
CMD ["main.lambda_handler"]
