#!/bin/bash

# Define the package directory and the deployment package name
PACKAGE_DIR="package"
DEPLOYMENT_PACKAGE="lambda_function_package.zip"

# Clean up any previous package directory and deployment package
rm -rf $PACKAGE_DIR
rm -f $DEPLOYMENT_PACKAGE

# Create a package directory
mkdir $PACKAGE_DIR

# Install dependencies into the package directory
pip3 install -r requirements.txt -t $PACKAGE_DIR

# Navigate to the package directory and create the deployment package zip file
cd $PACKAGE_DIR
zip -r ../$DEPLOYMENT_PACKAGE .

# Navigate back to the root directory
cd ..

# Add the lambda function code to the deployment package
zip -g $DEPLOYMENT_PACKAGE lambda_function.py
zip -g $DEPLOYMENT_PACKAGE serve_documentation.py
zip -g $DEPLOYMENT_PACKAGE register.py
zip -g $DEPLOYMENT_PACKAGE login.py
zip -g $DEPLOYMENT_PACKAGE social_login.py
zip -g $DEPLOYMENT_PACKAGE reset_password.py
zip -g $DEPLOYMENT_PACKAGE update_password.py
zip -g $DEPLOYMENT_PACKAGE buy_subscription.py
zip -g $DEPLOYMENT_PACKAGE cancel_subscription.py
zip -g $DEPLOYMENT_PACKAGE README.md
zip -g $DEPLOYMENT_PACKAGE openapi.yaml

echo "Deployment package $DEPLOYMENT_PACKAGE created successfully."

