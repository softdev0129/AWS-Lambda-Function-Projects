#!/bin/bash

# Function to check if jq is installed
check_jq_installed() {
  if ! command -v jq &> /dev/null
  then
      echo "jq could not be found. Please install jq to proceed."
      exit 1
  fi
}

# Check if jq is installed
check_jq_installed

# Variables
REPOSITORY_NAME="my-lambda-function"
IMAGE_TAG="latest"
LOCAL_PORT=9000
EMAIL="ddo.asare@gmail.com"

RDS_USERNAME="postgres"
RDS_PASSWORD="GWtxSGM4swxxhN3fMHRH"
RDS_ENDPOINT="database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com"
RDS_DB_NAME="plf_db"
FIREBASE_API_KEY="AIzaSyAKFzkKZF4cyzzDFv_JiusmBl_lNj1Wwbo"
FROM_EMAIL="no-reply@primeleadfinder.com"
SENDGRID_API_KEY="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"
AWS_ACCESS_KEY_ID="AKIARTTYG4LM3EINIOE6"
AWS_SECRET_ACCESS_KEY="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"

# Firebase credentials (trimmed for brevity)
FIREBASE_CREDENTIALS='{
  "type": "service_account",
  "project_id": "flp-app-93d33",
  "private_key_id": "d1f1d53101900760ff0b28938ed15095a4724070",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/6rhRgs/e2Cxg\ns4IbGtSpzR868/B+B7n4Ch9S+xEHRdP7vPzBLtdEvmY+u2GLs0rsd9BYWbLVl0Rp\nbaFHS/yxQ8L/OqOEiuoODnoiuop4r+mkqhoZUy2kP7T0yVe9EXItFEl0PJC4Ifcc\nQLVs95rwlqysOGvHBpjTyqNC599LZeIw0zkwfTXMjGE4zMsbs97iWcL+LuJ2J+Au\nW4QT7SAhAa+9THNyDlfxxDCTiUGslfz2/7N0DPDx7IAbL1UFsGVDOpqGspsT24KH\nGzMjEfgxrHbNc+8VQpi8uYPyKmNHp5Z7vpaVMXir1u3kYlKNXsRp8k31/gyKtAXB\np87mfsTjAgMBAAECggEAXRUwqeQ7AzgxKgPWzmOwktz40USgt9fyhJIQSFSamT7u\nhrJOmzonUeHRQIrs0G+5HsEsDbYPzZXtKf9w0l5SJP4bNWSRC8e+puuxpGd6oveb\naHDScMcNo5T8pR+EzSCJksC8scJwZMagjpT6Cex8O0WxYWSKLcGO3WZy0hAZlvzu\ndnq8tsLl7mKkOYiuSckm0G4RV6M2lNTHWNFIc1UyvKXNEKQDvnnbq38g5e2ioliX\nvzGKD13LU1HJUJrnCnTYmZTC4yQXAJwvEEEKIDNb/OPraDqTHx/nR17VGYtoQfrr\nSMYKMv1t/IHuj1ejEA96fbED1GLK7alLHVnRBZqbKQKBgQD5hPEX7+kri80P3AZX\ndvLhfGzgbPiBlC832NE2mkV4r4Bpfxj8IE/5udVm01yZ1E/DA26yygo3VI5EZ/Tm\nugT/2VJFeYcPEBRxlPXeDzjD8rm/hXt/49UDkMxiUBXu2TOP92V6WceD/SWiEb9e\nWdDKe5c7l7pKj4g/FhF9f3Y1aQKBgQDE5sdWbEsE8n8mGKlY0y0S/Esjw7uobXy9\nyuPgzR1SlRooHUr3wqThfdIW5qWYEl0z8vfXu1TU0b6hm+Dz41WVSio1P3+Bhe2v\nvOGys0Og7dPfLJJg7q2zAiqyyVufi0OXmnstg+FeYlX1T7i1MxAfzGGK8guxc4Ma\nwAUiZLqiawKBgQCWmRF2tBtUaA19a/v74FQZmiKQldSrSMfy+g7T2OrjO3HSup5W\n1h3PCMVvSVSTl9wIRNMUX/MokAVJ7kCW3WFVFlKckgvdIIRmRVTcEO3e/mnz2Vm/\nx7/yZfulvtZuEXQYiWYbIYLU+/4xwmpxRN5Kx6twkVQj2luOUACAcWTkOQKBgD0/\nlE47zXIyhH6zOSpaNjErravoXN1dgWoATLZG15Iyszo7MnCzaVqDKvDYujX9sGRS\ndenzacXxoJzgwi7bTmnr8gkyQVVm9bKuzH4r6SOMF1XapYXleL6wM9v9arTMOzBT\na3GTDm2vpRFzxP8IbUGW79iqxhxi1CtkA7TZJH0VAoGABI2R8tpWeCgcGuO8G/JP\nWukKAa8PtK/nKy1A1dH5SEdlg+4PqR0taxyHtH1/6rxVg6HOHl9Z9UMGILgVPp2r\nDmlusLONZgoNNp6j4lHwkHFz1+cHVum+03+/wA38HFXUmTfvCX432bqTyvJi/Fna\nqNHKkeX24sAxK4xbM/t6STg=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-ztyaw@flp-app-93d33.iam.gserviceaccount.com",
  "client_id": "103972125751531977422",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ztyaw@flp-app-93d33.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'
# Step 1: Build the Docker image with the correct platform
echo "Building the Docker image..."
docker build --platform linux/arm64 -t $REPOSITORY_NAME .

# Step 2: Run the Docker container locally with environment variables
echo "Running the Docker container locally..."
docker run --platform linux/arm64 -p $LOCAL_PORT:8080 \
  -e FIREBASE_CREDENTIALS="$FIREBASE_CREDENTIALS" \
  -e STRIPE_API_KEY="$STRIPE_API_KEY" \
  -e SENDGRID_API_KEY="$SENDGRID_API_KEY" \
  -e RDS_USERNAME="$RDS_USERNAME" \
  -e RDS_PASSWORD="$RDS_PASSWORD" \
  -e RDS_ENDPOINT="$RDS_ENDPOINT" \
  -e RDS_DB_NAME="$RDS_DB_NAME" \
  -e FIREBASE_API_KEY="$FIREBASE_API_KEY" \
  -e FROM_EMAIL="$FROM_EMAIL" \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  $REPOSITORY_NAME:latest &

# Wait for the container to start
sleep 10

# Function to print a divider
print_divider() {
  echo "----------------------------------------"
}

# Send Password Reset Email
print_divider
echo "Sending password reset email..."
RESET_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:$LOCAL_PORT/2015-03-31/functions/function/invocations" \
  -d "{\"path\": \"/customer/auth/resetPassword\", \"body\": \"{\\\"email\\\": \\\"${EMAIL}\\\"}\"}")

RESET_BODY=$(echo "${RESET_RESPONSE}" | sed '$d')
RESET_STATUS=$(echo "${RESET_RESPONSE}" | tail -n1)

echo "Reset Password Response Body: ${RESET_BODY}"
echo "Reset Password Response Status: ${RESET_STATUS}"

# Step 4: Stop the Docker container
echo "Stopping the Docker container..."
docker ps | grep $REPOSITORY_NAME | awk '{print $1}' | xargs docker stop
