# Marchcroft Company Backend API

**AWS Lambda • Python • Serverless REST API**

Official backend API for https://marchcroft.com/\
Built using Python and deployed on AWS Lambda to provide a scalable,
secure, and cost‑efficient serverless architecture.

------------------------------------------------------------------------

## Overview

This backend powers the Marchcroft company website and provides:

-   RESTful API endpoints via Amazon API Gateway
-   Serverless execution using AWS Lambda
-   Lightweight Python-based business logic
-   Secure and scalable architecture
-   Cloud-native deployment model

Designed for reliability, performance, and long-term maintainability.

------------------------------------------------------------------------

## Architecture

Website (Frontend)\
↓\
Amazon API Gateway\
↓\
AWS Lambda (Python Runtime)\
↓\
Business Logic Layer\
↓\
(Optional) External Services / Database

------------------------------------------------------------------------

## Project Structure

    .
    ├── lambda_function.py     # Lambda entry point
    ├── requests/              # HTTP client
    ├── urllib3/
    ├── certifi/
    ├── charset_normalizer/
    ├── idna/
    ├── bin/
    ├── requirements
    ├── README.md
    ├── .gitignore
    └── *.dist-info

All dependencies are packaged for direct AWS Lambda ZIP deployment.

------------------------------------------------------------------------

## Lambda Configuration

Runtime: - Python 3.10+

Handler:

    lambda_function.lambda_handler

------------------------------------------------------------------------

## Deployment Instructions

### 1️⃣ Create ZIP Package

``` bash
zip -r lambda.zip .
```

### 2️⃣ Upload to AWS Lambda

-   Create or update Lambda function

-   Upload `lambda.zip`

-   Set handler:

        lambda_function.lambda_handler

### 3️⃣ Connect API Gateway

-   Create HTTP API or REST API
-   Integrate with Lambda
-   Deploy stage (e.g., production)

------------------------------------------------------------------------

## Dependencies

-   requests
-   urllib3
-   certifi
-   charset-normalizer
-   idna

No external Lambda layers required.

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

Add additional permissions only if integrating: - S3 - RDS - DynamoDB -
Secrets Manager

Follow least‑privilege principle.

------------------------------------------------------------------------

## Performance Recommendations

-   Memory: 256MB--512MB recommended
-   Timeout: 10--30 seconds depending on workload
-   Enable API Gateway throttling
-   Implement structured logging

------------------------------------------------------------------------

## Security Best Practices

-   Validate and sanitize all inputs
-   Use HTTPS-only API Gateway endpoints
-   Store secrets in AWS Secrets Manager
-   Enable IAM role-based access
-   Monitor via CloudWatch logs and metrics

------------------------------------------------------------------------

## Scalability

-   Fully serverless
-   Auto-scales with Lambda concurrency
-   Cost-efficient pay‑per‑execution model

------------------------------------------------------------------------

## Example Error Response

``` json
{
  "status": "error",
  "message": "Invalid request",
  "details": {}
}
```

------------------------------------------------------------------------

## License

Specify license (MIT, Proprietary, Commercial, etc.)

------------------------------------------------------------------------

## Disclaimer

This backend API supports Marchcroft's web platform.\
Ensure secure configuration and compliance with applicable regulations
and company policies.
