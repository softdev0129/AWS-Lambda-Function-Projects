# Website Contact Details Extractor

**AWS Lambda • Python • Serverless Web Data Extraction**

A serverless data extraction system built with Python and deployed on
AWS Lambda.\
This project extracts contact details (emails, phone numbers, and
related metadata) from websites and stores or processes the results for
downstream workflows.

Designed for scalable, automated web data collection.

------------------------------------------------------------------------

## Project Overview

This system:

-   Crawls and analyzes website content
-   Extracts contact details (emails, phone numbers)
-   Supports PostgreSQL integration (pg8000)
-   Tracks job execution via queue system
-   Runs as an AWS Lambda function
-   Packaged for direct ZIP deployment

Optimized for automation and scalable scraping workloads.

------------------------------------------------------------------------

## Architecture

Trigger (API Gateway / EventBridge)\
↓\
AWS Lambda (Python Runtime)\
↓\
Website Scraper\
↓\
Contact Extraction Logic\
↓\
Database (PostgreSQL)\
↓\
Job Queue Tracker\
↓\
CloudWatch Logs

------------------------------------------------------------------------

## Project Structure

    .
    ├── extract-contact-details.py    # Main extraction logic
    ├── event_action.py               # Event routing logic
    ├── jobqueue_tracker.py           # Job tracking
    ├── pg8000/                       # PostgreSQL driver
    ├── python_dotenv/
    ├── requests/
    ├── urllib3/
    ├── asn1crypto/
    ├── scramp/
    ├── six.py
    ├── requirements
    ├── README.md
    └── *.dist-info

All dependencies are bundled for AWS Lambda ZIP deployment.

------------------------------------------------------------------------

## Lambda Configuration

Runtime: - Python 3.10+

Handler:

    extract-contact-details.lambda_handler

(Adjust if entry function differs)

------------------------------------------------------------------------

## Deployment

### ZIP Deployment

``` bash
zip -r lambda.zip .
```

Upload to AWS Lambda and configure handler.

------------------------------------------------------------------------

## Database Configuration

Environment variables example:

    DB_HOST=
    DB_PORT=
    DB_NAME=
    DB_USER=
    DB_PASSWORD=

Ensure Lambda is deployed within appropriate VPC for RDS connectivity.

------------------------------------------------------------------------

## Core Technologies

-   Python 3.10+
-   AWS Lambda
-   pg8000 (PostgreSQL driver)
-   Requests (HTTP client)
-   dotenv (environment management)
-   Serverless job tracking

------------------------------------------------------------------------

## Features

-   Automated website scanning
-   Email and phone extraction
-   Duplicate handling
-   Job tracking system
-   Database persistence
-   Scalable execution model

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

If using database or other AWS services: - Add respective permissions
following least-privilege principle

------------------------------------------------------------------------

## Performance Recommendations

-   Memory: 512MB--1024MB recommended
-   Timeout: 60--120 seconds depending on crawl size
-   Implement rate limiting for ethical scraping
-   Use retry/backoff strategies

------------------------------------------------------------------------

## Security & Compliance

-   Extract only publicly available information
-   Respect website robots.txt policies
-   Avoid aggressive scraping patterns
-   Secure database credentials using AWS Secrets Manager

------------------------------------------------------------------------

## Scalability

-   Fully serverless architecture
-   Auto-scales with Lambda concurrency
-   Suitable for bulk contact extraction workflows

------------------------------------------------------------------------

## License

Specify license (MIT, Proprietary, Commercial, etc.)

------------------------------------------------------------------------

## Disclaimer

This extraction tool is intended for collecting publicly available
contact information.\
Users are responsible for compliance with applicable data protection
laws and website terms of service.
