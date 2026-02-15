# Fiverr Gig Reviews Scraper

**AWS Lambda (Python 3.x)**

A serverless AWS Lambda function written in Python that scrapes publicly
available Fiverr gig reviews and returns structured JSON data. The
project is packaged for direct ZIP deployment with all dependencies
bundled.

------------------------------------------------------------------------

## Project Overview

This Lambda function:

-   Scrapes public Fiverr gig review data
-   Extracts rating, reviewer, review text, and date
-   Returns structured JSON output
-   Can be extended to store data in RDS (PostgreSQL via psycopg2), S3,
    or DynamoDB

Optimized for AWS Lambda ZIP deployment.

------------------------------------------------------------------------

## Current Project Structure

    .
    ├── lambda_function.py
    ├── fiverr_api/
    ├── bs4/
    ├── requests/
    ├── psycopg2/
    ├── psycopg2_binary.libs/
    ├── certifi/
    ├── charset_normalizer/
    ├── html5lib/
    ├── idna/
    ├── six/
    ├── soupsieve/
    ├── urllib3/
    ├── webencodings/
    └── *.dist-info

This structure is ready for direct AWS Lambda ZIP upload.

------------------------------------------------------------------------

## Lambda Configuration

Runtime: Python 3.10 (or compatible)

Handler:

    lambda_function.lambda_handler

------------------------------------------------------------------------

## Example Event

``` json
{
  "gig_url": "https://www.fiverr.com/username/service-name",
  "max_pages": 2
}
```

------------------------------------------------------------------------

## Example Response

``` json
{
  "status": "success",
  "reviews": [
    {
      "review_id": "123456",
      "rating": 5,
      "review_text": "Outstanding work and fast delivery.",
      "reviewer": "buyer_username",
      "created_at": "2026-02-14"
    }
  ],
  "total_reviews": 20
}
```

------------------------------------------------------------------------

## Deployment (ZIP Method)

1.  Create ZIP file:

``` bash
zip -r lambda.zip .
```

2.  Upload to AWS Lambda console.

3.  Set handler:

```{=html}
<!-- -->
```
    lambda_function.lambda_handler

------------------------------------------------------------------------

## Optional: PostgreSQL Integration

Included dependency: psycopg2

Environment variables example:

    DB_HOST=
    DB_PORT=
    DB_NAME=
    DB_USER=
    DB_PASSWORD=

Ensure Lambda is configured inside correct VPC if connecting to RDS.

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

------------------------------------------------------------------------

## Performance Notes

-   Increase timeout to 30--60 seconds if scraping multiple pages.
-   Recommended memory: 512MB+ when using psycopg2.
-   Avoid high-frequency scraping.

------------------------------------------------------------------------

## Security & Compliance

-   Scrape publicly available data only.
-   Respect platform policies and rate limits.
-   Follow Fiverr's Terms of Service.

------------------------------------------------------------------------

## License

Specify your license here.

------------------------------------------------------------------------

## Disclaimer

This software is provided for educational and analytical purposes.\
Users are responsible for ensuring compliance with Fiverr's Terms of
Service and applicable regulations.
