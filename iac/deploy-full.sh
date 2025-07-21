#!/bin/bash

# LegiSync Deployment Script
# This handles the frontend deployment and checks for backend deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

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

echo "🚀 LegiSync Frontend Deployment - $ENVIRONMENT Environment"
echo "========================================================"

# Step 1: Check prerequisites
print_step "Checking prerequisites..."

if [ ! -f "terraform.tfvars" ]; then
    print_error "terraform.tfvars not found!"
    print_warning "Copy terraform.tfvars.example to terraform.tfvars and fill in your values"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed"
    exit 1
fi

# Step 2: Check backend deployment
print_step "Backend Deployment Check..."

BACKEND_URL=$(grep "backend_url" ${ENVIRONMENT}.tfvars | cut -d'"' -f2)

if [[ "$BACKEND_URL" == *"localhost"* ]] || [[ "$BACKEND_URL" == *"your-"* ]]; then
    print_warning "Backend URL appears to be a placeholder: $BACKEND_URL"
    echo
    print_step "Please deploy your backend first:"
    echo "1. 🎨 Deploy to Render:"
    echo "   - Go to https://dashboard.render.com/"
    echo "   - Connect your GitHub repo"
    echo "   - Set Root Directory: backend"
    echo "   - Set Build Command: pip install -r requirements.txt"
    echo "   - Set Start Command: uvicorn app:app --host 0.0.0.0 --port \$PORT"
    echo
    echo "2. 📝 Update ${ENVIRONMENT}.tfvars with your backend URL"
    echo "3. 🔄 Run this script again"
    echo
    read -p "Have you deployed your backend and updated the URL? (y/N): " response
    
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_warning "Please deploy your backend first, then run this script again"
        exit 1
    fi
else
    print_status "Backend URL configured: $BACKEND_URL"
fi

# Step 3: Deploy infrastructure with Terraform
print_step "Deploying infrastructure with Terraform..."

terraform init
terraform validate
terraform fmt

print_status "Planning deployment for $ENVIRONMENT..."
terraform plan -var-file="${ENVIRONMENT}.tfvars" -out="${ENVIRONMENT}.tfplan"

echo
print_warning "Review the plan above. Do you want to apply these changes? (y/N)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    terraform apply "${ENVIRONMENT}.tfplan"
    rm -f "${ENVIRONMENT}.tfplan"
    
    print_status "✅ Deployment completed successfully!"
    
    # Show outputs
    echo
    print_status "📊 Deployment Information:"
    terraform output -json | jq -r '.deployment_info.value | to_entries[] | "\(.key): \(.value)"'
    
    # Get frontend URL
    FRONTEND_URL=$(terraform output -raw vercel_deployment_url 2>/dev/null || echo "")
    
    echo
    print_status "🎉 Your LegiSync app is deployed!"
    echo "Frontend: $FRONTEND_URL"
    echo "Backend:  $BACKEND_URL"
    
    # Step 4: Data ingestion reminder
    echo
    print_step "Next Steps:"
    echo "1. ✅ Infrastructure deployed"
    echo "2. ✅ Frontend deployed to Vercel" 
    echo "3. ✅ Backend deployed to Render"
    echo "4. 🔄 Run data ingestion:"
    echo "   cd ../backend"
    echo "   python ingest.py"
    echo "5. 🧪 Test your application:"
    echo "   Open: $FRONTEND_URL"
    
else
    print_warning "Deployment cancelled"
    rm -f "${ENVIRONMENT}.tfplan"
fi
