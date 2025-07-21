#!/bin/bash

# LegiSync Deployment Script
# Usage: ./deploy.sh [dev|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
if [ $# -eq 0 ]; then
    print_error "Please specify environment: dev or prod"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

ENVIRONMENT=$1

if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
    print_error "Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

print_status "Deploying LegiSync to $ENVIRONMENT environment..."

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    print_error "terraform.tfvars not found!"
    print_warning "Copy terraform.tfvars.example to terraform.tfvars and fill in your values"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed"
    print_warning "Install Terraform from https://terraform.io/downloads"
    exit 1
fi

# Initialize Terraform (safe to run multiple times)
print_status "Initializing Terraform..."
terraform init

# Validate configuration
print_status "Validating Terraform configuration..."
terraform validate

# Format configuration files
print_status "Formatting Terraform files..."
terraform fmt

# Plan the deployment
print_status "Planning deployment for $ENVIRONMENT..."
terraform plan -var-file="${ENVIRONMENT}.tfvars" -out="${ENVIRONMENT}.tfplan"

# Ask for confirmation
echo
print_warning "Review the plan above. Do you want to apply these changes? (y/N)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    # Apply the plan
    print_status "Applying Terraform configuration..."
    terraform apply "${ENVIRONMENT}.tfplan"
    
    # Clean up plan file
    rm -f "${ENVIRONMENT}.tfplan"
    
    print_status "Deployment completed successfully!"
    
    # Show outputs
    echo
    print_status "Deployment information:"
    terraform output -json | jq -r '.deployment_info.value | to_entries[] | "\(.key): \(.value)"'
    
    echo
    print_status "Next steps:"
    echo "1. Deploy your backend to Railway, Render, or another service"
    echo "2. Update the backend_url in ${ENVIRONMENT}.tfvars with your backend URL"
    echo "3. Run this script again to update the frontend with the correct backend URL"
    echo "4. Run your data ingestion script to populate the Pinecone index"
    
else
    print_warning "Deployment cancelled"
    rm -f "${ENVIRONMENT}.tfplan"
fi
