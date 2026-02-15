# Serverless Email Operations API

**AWS Lambda • API Gateway • SMTP & IMAP Integration**

A production-ready AWS Lambda project that efficiently manages email
operations using standard **SMTP** and **IMAP** protocols.\
This API enables sending emails, retrieving messages, saving drafts,
moving emails to trash, and permanently deleting emails.

Designed for secure, scalable, and cloud-native email processing.

------------------------------------------------------------------------

## Architecture Overview

Client Application\
↓\
Amazon API Gateway\
↓\
AWS Lambda\
↓\
SMTP / IMAP Server (Gmail, Outlook, Custom Mail Server)

------------------------------------------------------------------------

## Base API Endpoint

    https://d6aljed0n5.execute-api.eu-west-1.amazonaws.com/v1

------------------------------------------------------------------------

# API Endpoints

------------------------------------------------------------------------

## 1️⃣ Send Email

### Endpoint

    POST /send-email

### Description

Sends email using provided SMTP credentials.\
Supports password-based authentication and OAuth2.

### Sample Payload (Password Authentication)

``` json
{
  "smtpCredentials": {
    "host": "smtp.example.com",
    "port": 587,
    "secure": false,
    "auth": {
      "user": "source_email",
      "pass": "password"
    }
  },
  "mailOptions": {
    "from": "source_email",
    "to": ["recipient1@example.com"],
    "cc": ["cc@example.com"],
    "subject": "Test Email",
    "text": "Plain text content",
    "html": "<strong>HTML content</strong>",
    "attachments": [
      {
        "filename": "file.txt",
        "content": "Base64EncodedContent",
        "encoding": "base64"
      }
    ]
  }
}
```

### Sample Payload (OAuth2)

``` json
{
  "smtpCredentials": {
    "host": "smtp.gmail.com",
    "port": 587,
    "secure": false,
    "auth": {
      "user": "source_email",
      "accessToken": "access_token",
      "refreshToken": "refresh_token",
      "type": "OAuth2"
    }
  },
  "mailOptions": {}
}
```

------------------------------------------------------------------------

## 2️⃣ Retrieve Emails

### Endpoint

    POST /retrieve-emails

### Description

Retrieves paginated email messages from a specified mailbox path (e.g.,
INBOX, Sent).

### Sample Payload

``` json
{
  "smtpCredentials": {
    "host": "imap.example.com",
    "port": 993,
    "secure": true,
    "auth": {
      "user": "email@example.com",
      "pass": "password"
    }
  },
  "path": "INBOX",
  "page": 1,
  "pageSize": 10
}
```

------------------------------------------------------------------------

## 3️⃣ Save Email to Draft

### Endpoint

    POST /save-to-draft

### Description

Creates and saves an email as a draft in the Drafts mailbox.

### Sample Payload

``` json
{
  "smtpCredentials": {
    "host": "imap.example.com",
    "port": 993,
    "secure": true,
    "auth": {
      "user": "email@example.com",
      "pass": "password"
    }
  },
  "mailOptions": {
    "from": "email@example.com",
    "to": ["recipient@example.com"],
    "subject": "Draft Email",
    "text": "Draft content"
  }
}
```

------------------------------------------------------------------------

## 4️⃣ Move Email to Trash

### Endpoint

    POST /move-to-trash

### Description

Moves an email from a specified mailbox to the Trash folder using UID.

### Sample Payload

``` json
{
  "smtpCredentials": {},
  "uid": 2,
  "path": "Sent"
}
```

------------------------------------------------------------------------

## 5️⃣ Empty Trash (Permanent Delete)

### Endpoint

    POST /empty-trash

### Description

Permanently deletes an email from the Trash folder using UID.

### Sample Payload

``` json
{
  "smtpCredentials": {},
  "uid": 1
}
```

------------------------------------------------------------------------

# Authentication Methods

Supported:

-   SMTP Password Authentication
-   IMAP Password Authentication
-   OAuth2 (Gmail, Outlook compatible providers)

------------------------------------------------------------------------

# Security Best Practices

-   Use OAuth2 whenever possible.
-   Do not log raw credentials.
-   Use HTTPS-only API Gateway.
-   Restrict IAM permissions using least-privilege principle.
-   Store sensitive data in AWS Secrets Manager or encrypted environment
    variables.

------------------------------------------------------------------------

# AWS Configuration

## Lambda Runtime

-   Node.js or Python (based on implementation)

## Required IAM Permissions

-   CloudWatch Logs access
-   VPC access (if required)
-   Secrets Manager (optional)

------------------------------------------------------------------------

# Error Handling

Standard error response:

``` json
{
  "status": "error",
  "message": "Error description",
  "details": {}
}
```

------------------------------------------------------------------------

# Performance & Scalability

-   Fully serverless architecture
-   Auto-scales with AWS Lambda concurrency
-   Suitable for SaaS integrations and multi-tenant applications

------------------------------------------------------------------------

# Compliance & Responsibility

This API acts as a middleware layer between client applications and
email servers.\
Users are responsible for complying with their email provider's terms of
service and security policies.

------------------------------------------------------------------------

# License

Specify your license here (MIT, Proprietary, Commercial, etc.).

------------------------------------------------------------------------

# Disclaimer

This software is provided as-is.\
Proper security practices and credential management are required when
using email authentication.
