# Upremleads Admin Backend API

**AWS Lambda • Python • PostgreSQL (RDS)**

Administrative backend API for the Upremleads platform.\
Built using Python and deployed on AWS Lambda with Amazon RDS
(PostgreSQL) integration.

This service provides:

-   Data retrieval with pagination
-   Duplicate filtering
-   Batch updates for LinkedIn & Fiverr records
-   Static frontend file serving
-   CORS-enabled REST API

------------------------------------------------------------------------

## Architecture

Admin Frontend\
↓\
Amazon API Gateway\
↓\
AWS Lambda (Python Runtime)\
↓\
PostgreSQL (Amazon RDS)\
↓\
CloudWatch Logging

------------------------------------------------------------------------

## Project Structure

    .
    ├── lambda_function.py       # Lambda entry point
    ├── pg8000/                  # PostgreSQL driver
    ├── scramp/
    ├── asn1crypto/
    ├── dateutil/
    ├── six.py
    ├── requirements
    ├── README.md
    └── *.dist-info

All dependencies are bundled for direct AWS Lambda ZIP deployment.

------------------------------------------------------------------------

## Lambda Configuration

Runtime: - Python 3.10+

Handler:

    lambda_function.lambda_handler

------------------------------------------------------------------------

## API Behavior

### GET `/api`

Retrieves paginated Fiverr/LinkedIn records.

Query Parameters:

-   `page` (default: 1)
-   `limit` (default: 10)
-   `showDuplicates` (0 or 1)

Response:

``` json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

------------------------------------------------------------------------

### POST `/api`

Batch updates records.

Expected body format:

``` json
[
  {
    "id": 1,
    "columnName": "linkedin_profile",
    "newValue": "https://linkedin.com/in/example"
  }
]
```

Supports:

-   Updating `is_duplicate`
-   Updating existing LinkedIn records
-   Creating new LinkedIn records if not existing

------------------------------------------------------------------------

## Static File Serving

If the request path does not match `/api`, the Lambda attempts to serve
static files from the `build/` directory.

Useful for:

-   Admin dashboard hosting
-   Single Lambda full-stack deployment

------------------------------------------------------------------------

## Deployment

### ZIP Deployment

``` bash
zip -r lambda.zip .
```

Upload to AWS Lambda and configure handler.

------------------------------------------------------------------------

## Database Configuration

⚠️ Important: Do NOT hardcode credentials in production.

Recommended environment variables:

    DB_HOST=
    DB_USER=
    DB_PASSWORD=
    DB_NAME=
    DB_PORT=5432

Use AWS Secrets Manager for secure credential storage.

Ensure Lambda runs inside correct VPC for RDS access.

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

If using Secrets Manager: - secretsmanager:GetSecretValue

------------------------------------------------------------------------

## Security Considerations

-   Validate column names before dynamic SQL execution
-   Use parameterized queries (already implemented for values)
-   Avoid exposing database credentials in source code
-   Restrict CORS in production environments
-   Apply least-privilege IAM roles

------------------------------------------------------------------------

## Performance Recommendations

-   Memory: 512MB+ recommended
-   Timeout: 30--60 seconds
-   Use connection pooling if scaling heavily
-   Add indexing to frequently queried columns

------------------------------------------------------------------------

## Scalability

-   Fully serverless architecture
-   Auto-scales with Lambda concurrency
-   Suitable for admin dashboards and internal tools

------------------------------------------------------------------------

## License

Proprietary -- Upremleads

------------------------------------------------------------------------

## Disclaimer

This backend API is intended for administrative use.\
Ensure secure configuration and compliance with internal security
policies.
