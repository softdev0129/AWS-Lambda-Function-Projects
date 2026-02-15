# Serverless Projects Collection

**AWS Lambda • Python | Node.js • Automation & Data Systems**

This repository contains multiple AWS Lambda (Python | Node.js) backend projects
focused on automation, scraping, SaaS APIs, job processing, and
AI-assisted workflows.

All projects are designed using a serverless architecture and packaged
for direct AWS Lambda deployment.

------------------------------------------------------------------------

## Projects Overview

### 1. Email Client API

-   Send emails (SMTP)
-   Retrieve emails (IMAP)
-   Save drafts
-   Delete/move emails

### 2. Fiverr Gigs Review Scraper

-   Scrapes Fiverr gig reviews
-   Processes structured data

### 3. Google Scrape Industries

-   Extracts industry-related Google data

### 4. Google Scrape Industries (Async)

-   Async scalable data extraction using HTTPX

### 5. Job Queue Site

-   Serverless background job processor

### 6. Marchcroft API

-   Backend API for company website

### 7. PLF Customer API

-   Authentication
-   Billing & subscriptions
-   Social login

### 8. PLF Data API

-   Internal data services backend

### 9. Fiverr Scheduled Job

-   EventBridge-triggered scraping system

### 10. Send Proposal Upwork

-   AI-generated Upwork proposals

### 11. Send Upwork Job Notifications

-   Automated Upwork job monitoring

### 12. Upremleads Admin

-   Admin backend with PostgreSQL

### 13. Upwork Job Offer Automation

-   AI-powered job offer responses

### 14. Website Extract Contact Details

-   Extracts emails and phone numbers from websites

------------------------------------------------------------------------

## Common Architecture

Trigger (API Gateway / EventBridge)\
↓\
AWS Lambda (Python)\
↓\
Business Logic\
↓\
Database / External APIs\
↓\
CloudWatch

------------------------------------------------------------------------

## Deployment

``` bash
zip -r lambda.zip .
```

Upload to AWS Lambda and configure the handler.

------------------------------------------------------------------------

## Technologies

-   Python 3.10+
-   AWS Lambda
-   PostgreSQL
-   Requests / HTTPX
-   OpenAI API
-   API Gateway
-   EventBridge
-   CloudWatch

------------------------------------------------------------------------

## Security

-   Use AWS Secrets Manager
-   Avoid hardcoded credentials
-   Apply least-privilege IAM roles
-   Respect third-party platform policies

------------------------------------------------------------------------

## Disclaimer

These projects are for backend automation and services.\
Users must ensure compliance with applicable policies and regulations.
