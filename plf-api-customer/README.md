# PLF Customer Backend API

**AWS Lambda • Python • Serverless REST Architecture**

Official backend API for **Prime Lead Finder**\
Website: https://primeleadfinder.com/

This project is a serverless customer-facing backend built using Python
and deployed on AWS Lambda.\
It provides authentication, billing, subscription management, and
customer account services.

------------------------------------------------------------------------

## Architecture Overview

Frontend (PrimeLeadFinder.com) ↓ Amazon API Gateway ↓ AWS Lambda (Python
Runtime) ↓ Business Logic Modules ↓ Firebase Auth / Stripe / Database

------------------------------------------------------------------------

## Project Structure

    .
    ├── auth/                   # Authentication logic
    ├── billing/                # Subscription & billing services
    ├── customer/               # Customer endpoints
    ├── db/                     # Database utilities
    ├── decorators/             # Auth & middleware decorators
    ├── utils/                  # Shared helpers
    ├── tests/                  # Test scripts
    ├── main.py                 # Lambda entry point
    ├── event_type_enum.py
    ├── requirements
    ├── Dockerfile
    ├── buildspec.yml
    └── deployment scripts

------------------------------------------------------------------------

## Lambda Configuration

Runtime: - Python 3.10+

Handler:

    main.lambda_handler

------------------------------------------------------------------------

# API Documentation

## Register User

**POST** `/customer/auth/register`

``` json
{
    "email": "user@example.com",
    "password": "examplepassword"
}
```

------------------------------------------------------------------------

## Login User

**POST** `/customer/auth/login`

``` json
{
    "email": "user@example.com",
    "password": "examplepassword",
    "remember_me": true
}
```

------------------------------------------------------------------------

## Update Password

**POST** `/customer/user/updatePassword`

Headers:

``` json
{
    "Authorization": "Bearer <FIREBASE_ID_TOKEN>"
}
```

Body:

``` json
{
    "current_password": "currentpassword",
    "new_password": "newpassword"
}
```

------------------------------------------------------------------------

## Reset Password

**POST** `/customer/auth/resetPassword`

``` json
{
    "email": "user@example.com"
}
```

------------------------------------------------------------------------

## Buy Subscription

**POST** `/customer/billing/buySubscription`

Headers:

``` json
{
    "Authorization": "Bearer <FIREBASE_ID_TOKEN>"
}
```

``` json
{
    "payment_method_id": "pm_xxx",
    "price_id": "price_xxx"
}
```

------------------------------------------------------------------------

## Cancel Subscription

**POST** `/customer/billing/cancelSubscription`

Headers:

``` json
{
    "Authorization": "Bearer <FIREBASE_ID_TOKEN>"
}
```

``` json
{
    "subscription_id": "sub_xxx"
}
```

------------------------------------------------------------------------

## Get Billing History

**GET** `/customer/billing/getBillingHistory`

Headers:

``` json
{
    "Authorization": "Bearer <FIREBASE_ID_TOKEN>"
}
```

------------------------------------------------------------------------

## Social Login

**POST** `/customer/auth/socialLogin`

Google:

``` json
{
    "provider": "google",
    "id_token": "GOOGLE_ID_TOKEN"
}
```

LinkedIn:

``` json
{
    "provider": "linkedin",
    "access_token": "LINKEDIN_ACCESS_TOKEN"
}
```

------------------------------------------------------------------------

## AWS Lambda Permission Example

``` bash
aws lambda add-permission --function-name "plf_customer_api_lambda" --principal apigateway.amazonaws.com --action lambda:InvokeFunction
```

------------------------------------------------------------------------

## Deployment

### ZIP Deployment

``` bash
zip -r lambda.zip .
```

Upload to AWS Lambda and configure handler.

### Docker Deployment

Dockerfile included for container-based Lambda deployment.

------------------------------------------------------------------------

## Security Best Practices

-   Firebase ID token validation required for protected routes
-   Use AWS Secrets Manager for API keys
-   Apply least-privilege IAM roles
-   Enable structured logging via CloudWatch
-   Enforce HTTPS-only API Gateway

------------------------------------------------------------------------

## Scalability

-   Fully serverless architecture
-   Auto-scales with Lambda concurrency
-   Designed for SaaS multi-tenant workloads

------------------------------------------------------------------------

## License

Proprietary -- Prime Lead Finder

------------------------------------------------------------------------

## Reference

Original API documentation provided in project README
fileciteturn0file0
