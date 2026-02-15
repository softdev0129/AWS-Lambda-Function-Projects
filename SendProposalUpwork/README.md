# Upwork Proposal Automation System

**AWS Lambda • Python • AI-Assisted Proposal Generator**

A serverless automation system built with Python and deployed on AWS
Lambda to automatically generate and submit Upwork proposals.

This project integrates job scraping, AI-powered proposal generation,
authentication handling, and template management for scalable freelance
automation.

------------------------------------------------------------------------

## Project Overview

This system:

-   Retrieves Upwork job descriptions
-   Generates AI-powered proposals
-   Uses structured templates (JSON-based)
-   Handles login/authentication flows
-   Supports automated proposal submission
-   Runs in a serverless AWS Lambda environment

Designed for scalable freelance workflow automation.

------------------------------------------------------------------------

## Architecture

Event Trigger / API Gateway\
↓\
AWS Lambda (Python Runtime)\
↓\
Job Description Parser\
↓\
AI Proposal Generator (OpenAI)\
↓\
Template Engine\
↓\
Upwork Submission Handler\
↓\
CloudWatch Logging

------------------------------------------------------------------------

## Project Structure

    .
    ├── lambda_function.py             # Lambda entry point
    ├── proposal_generator.py          # Proposal generation logic
    ├── upwork_helper.py               # Upwork interaction utilities
    ├── login.py                       # Authentication handling
    ├── auth.py                        # Auth helpers
    ├── templates.py                   # Template loader
    ├── template/                      # Proposal templates
    ├── project_proposal_template.json
    ├── hourly_proposal_template.json
    ├── job_description_test_data.py
    ├── job_summary_response_example.json
    ├── openai/                        # OpenAI SDK
    ├── pydantic/                      # Validation models
    ├── requests/
    ├── httpx/
    ├── psycopg2/
    ├── aws_psycopg2/
    ├── tqdm/
    ├── requirements
    ├── test_lambda_function.py
    └── README.md

Dependencies are bundled for direct AWS Lambda ZIP deployment.

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

Upload to AWS Lambda and configure handler.

------------------------------------------------------------------------

## Environment Variables

Example configuration:

    OPENAI_API_KEY=
    UPWORK_EMAIL=
    UPWORK_PASSWORD=
    DB_HOST=
    DB_PORT=
    DB_NAME=
    DB_USER=
    DB_PASSWORD=

Use AWS Secrets Manager for production deployments.

------------------------------------------------------------------------

## Core Technologies

-   Python 3.10+
-   AWS Lambda
-   OpenAI API
-   Pydantic (Data validation)
-   Requests / HTTPX
-   psycopg2 (PostgreSQL)
-   Template-based proposal generation

------------------------------------------------------------------------

## Features

-   AI-generated personalized proposals
-   Structured JSON proposal templates
-   Hourly & fixed-price support
-   Job description summarization
-   Automated login/session handling
-   Optional database tracking

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

Add additional permissions only if integrating with: - RDS - S3 -
Secrets Manager

------------------------------------------------------------------------

## Performance Recommendations

-   Memory: 512MB--1024MB recommended
-   Timeout: 30--60 seconds
-   Enable structured logging
-   Use retry/backoff strategy for API calls

------------------------------------------------------------------------

## Security Considerations

-   Do not hardcode credentials
-   Store API keys securely
-   Implement rate limiting
-   Comply with Upwork Terms of Service
-   Avoid aggressive automation behavior

------------------------------------------------------------------------

## Scalability

-   Fully serverless
-   Auto-scales with Lambda concurrency
-   Suitable for multi-account automation workflows

------------------------------------------------------------------------

## Testing

Run local tests:

``` bash
python test_lambda_function.py
```

------------------------------------------------------------------------

## License

Specify your license (MIT, Proprietary, Commercial, etc.)

------------------------------------------------------------------------

## Disclaimer

This automation tool is intended for workflow assistance.\
Users are responsible for ensuring compliance with Upwork's policies and
terms of service.
