# Upwork Job Notification System

**AWS Lambda • Python • Automated Job Alerts**

A serverless job notification system built using Python and deployed on
AWS Lambda.\
This project monitors Upwork job listings and sends notifications based
on defined criteria.

Designed for scalable, automated freelance opportunity tracking.

------------------------------------------------------------------------

## Project Overview

This system:

-   Monitors Upwork job postings
-   Filters jobs based on defined rules/keywords
-   Stores results in PostgreSQL (psycopg2)
-   Sends notifications (email/webhook integration ready)
-   Runs in AWS Lambda environment
-   Packaged for direct ZIP deployment

------------------------------------------------------------------------

## Architecture

Scheduled Trigger (EventBridge)\
↓\
AWS Lambda (Python Runtime)\
↓\
Upwork Job Scraper\
↓\
Filter & Matching Logic\
↓\
Database (PostgreSQL)\
↓\
Notification System\
↓\
CloudWatch Logs

------------------------------------------------------------------------

## Project Structure

    .
    ├── lambda_function.py        # Lambda entry point
    ├── test.py                   # Local testing script
    ├── psycopg2/                 # PostgreSQL driver
    ├── aws_psycopg2/
    ├── requests/
    ├── urllib3/
    ├── certifi/
    ├── charset_normalizer/
    ├── idna/
    ├── requirements
    ├── README.md
    └── *.dist-info

Dependencies are bundled for AWS Lambda ZIP deployment.

------------------------------------------------------------------------

## Lambda Configuration

Runtime: - Python 3.10+

Handler:

    lambda_function.lambda_handler

------------------------------------------------------------------------

## Deployment

### ZIP Deployment

``` bash
zip -r lambda.zip .
```

Upload to AWS Lambda console and configure handler.

------------------------------------------------------------------------

## Scheduled Execution

Use Amazon EventBridge to schedule execution.

Example cron (every 30 minutes):

    cron(0/30 * * * ? *)

------------------------------------------------------------------------

## Database Configuration

Environment variables:

    DB_HOST=
    DB_PORT=
    DB_NAME=
    DB_USER=
    DB_PASSWORD=

Ensure Lambda runs inside proper VPC when connecting to RDS.

------------------------------------------------------------------------

## Core Technologies

-   Python 3.10+
-   AWS Lambda
-   PostgreSQL (psycopg2)
-   Requests (HTTP client)
-   Serverless scheduling

------------------------------------------------------------------------

## Features

-   Automated job scanning
-   Keyword-based filtering
-   Database tracking
-   Duplicate prevention
-   Notification-ready architecture
-   Lightweight deployment

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

If database or external services used: - Add corresponding permissions
following least-privilege principle

------------------------------------------------------------------------

## Performance Recommendations

-   Memory: 512MB recommended
-   Timeout: 30--60 seconds
-   Implement rate limiting
-   Avoid aggressive scraping intervals

------------------------------------------------------------------------

## Security Considerations

-   Do not hardcode credentials
-   Use AWS Secrets Manager
-   Comply with Upwork Terms of Service
-   Avoid high-frequency scraping

------------------------------------------------------------------------

## Scalability

-   Fully serverless
-   Auto-scales with Lambda concurrency
-   Suitable for multi-account monitoring systems

------------------------------------------------------------------------

## Testing

Run locally:

``` bash
python test.py
```

------------------------------------------------------------------------

## License

Specify license (MIT, Proprietary, Commercial, etc.)

------------------------------------------------------------------------

## Disclaimer

This automation tool is intended for monitoring publicly available job
listings.\
Users are responsible for ensuring compliance with Upwork's policies and
applicable regulations.
