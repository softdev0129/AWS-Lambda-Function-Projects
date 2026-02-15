#!/bin/bash

# Variables
REPOSITORY_NAME="plf_customer_api_lambda"
IMAGE_TAG="latest"
AWS_REGION="eu-west-1" # e.g., us-west-2
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY_NAME:$IMAGE_TAG"
LAMBDA_ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/your-lambda-role" # Replace with your Lambda execution role ARN

# Step 1: Build the Docker image
echo "Building the Docker image..."
docker build --platform linux/arm64 -t $REPOSITORY_NAME .

# Step 2: Authenticate Docker to Amazon ECR
echo "Authenticating Docker to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Create the ECR repository if it doesn't exist
echo "Creating ECR repository if it doesn't exist..."
aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $AWS_REGION > /dev/null 2>&1 || aws ecr create-repository --repository-name $REPOSITORY_NAME --region $AWS_REGION

# Step 4: Tag the Docker image
echo "Tagging the Docker image..."
docker tag $REPOSITORY_NAME:latest $ECR_URI

# Step 5: Push the Docker image to Amazon ECR
echo "Pushing the Docker image to Amazon ECR..."
docker push $ECR_URI

# Step 6: Create or update the Lambda function
echo "Creating or updating the Lambda function..."
aws lambda create-function --function-name $REPOSITORY_NAME \
  --package-type Image \
  --code ImageUri=$ECR_URI \
  --role $LAMBDA_ROLE_ARN \
  --region $AWS_REGION \
  --timeout 60 \
  --memory-size 128 > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "Lambda function created successfully."
else
  echo "Lambda function already exists, updating the function code..."
  aws lambda update-function-code --function-name $REPOSITORY_NAME --image-uri $ECR_URI --region $AWS_REGION
fi

echo "Deployment complete."
