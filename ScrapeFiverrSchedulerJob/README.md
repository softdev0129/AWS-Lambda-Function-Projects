# Fiverr Scheduled Scraper

**AWS Lambda • Python • Scheduled Background Job**

A serverless scheduled scraping system built using Python and deployed
on AWS Lambda.\
This project automatically scrapes Fiverr data on a scheduled basis and
processes results for storage or analytics.

------------------------------------------------------------------------

## Project Overview

This system:

-   Scrapes Fiverr data (gigs, reviews, or related data)
-   Runs as a scheduled AWS Lambda job
-   Supports proxy handling (SOCKS / PySocks)
-   Includes PostgreSQL support (psycopg2)
-   Designed for automated background execution
-   Packaged for direct ZIP deployment

Optimized for reliability, performance, and scalability.

------------------------------------------------------------------------

## Architecture

Amazon EventBridge (Scheduled Trigger) ↓ AWS Lambda (Python Runtime) ↓
Scraping Engine (Requests / BeautifulSoup / Trio) ↓ Proxy Layer (SOCKS
Support) ↓ Database (PostgreSQL) or External Storage ↓ CloudWatch Logs

------------------------------------------------------------------------

## Project Structure

    .
    ├── scrape_fiverr_web.py        # Main scraping logic
    ├── socks.py                    # SOCKS proxy implementation
    ├── sockshandler.py             # Proxy handler
    ├── typing_extensions.py
    ├── psycopg2/                   # PostgreSQL driver
    ├── aws_psycopg2/
    ├── bs4/                        # BeautifulSoup
    ├── requests/
    ├── trio/
    ├── trio_websocket/
    ├── urllib3/
    ├── attr/
    ├── sortedcontainers/
    ├── wsproto/
    ├── requirements
    ├── README.md
    └── *.dist-info

All dependencies are bundled for AWS Lambda ZIP deployment.

------------------------------------------------------------------------

## Lambda Configuration

Runtime: - Python 3.10+

Handler:

    scrape_fiverr_web.lambda_handler

------------------------------------------------------------------------

## Scheduled Execution

Configure using **Amazon EventBridge**:

-   Create Rule
-   Set schedule (cron or rate expression)
-   Target → Lambda function

Example cron (every hour):

    cron(0 * * * ? *)

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

Ensure Lambda runs inside appropriate VPC when connecting to RDS.

------------------------------------------------------------------------

## Proxy Support

Includes SOCKS proxy support using:

-   PySocks
-   Custom socks handler

Useful for:

-   IP rotation
-   Anti-throttling mitigation
-   Distributed scraping

------------------------------------------------------------------------

## IAM Permissions

Minimum required:

CloudWatch Logs: - logs:CreateLogGroup - logs:CreateLogStream -
logs:PutLogEvents

If database or S3 used: - Add corresponding permissions following least
privilege principle.

------------------------------------------------------------------------

## Performance Recommendations

-   Memory: 512MB--1024MB recommended
-   Timeout: 60--120 seconds depending on scraping volume
-   Implement request rate limiting
-   Use retry/backoff strategy
-   Avoid aggressive scraping frequency

------------------------------------------------------------------------

## Security & Compliance

-   Scrape publicly available data only
-   Respect Fiverr Terms of Service
-   Avoid bypassing authentication or CAPTCHA systems
-   Secure credentials via AWS Secrets Manager

------------------------------------------------------------------------

## Scalability

-   Fully serverless architecture
-   Auto-scales with Lambda concurrency
-   Suitable for multi-tenant scraping pipelines

------------------------------------------------------------------------

## Error Handling

Example response structure:

``` json
{
  "status": "error",
  "message": "Scraping failed",
  "details": {}
}
```

------------------------------------------------------------------------

## License

Specify your license (MIT, Proprietary, Commercial, etc.)

------------------------------------------------------------------------

## Disclaimer

This scraper is provided for automation and analytical purposes.\
Users are responsible for ensuring compliance with Fiverr's policies and
applicable regulations.
