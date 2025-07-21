#!/bin/bash

# Complete LegiSync Deployment Script
# This handles the full deployment workflow including backend URL management

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
    echo "Usage: $0 [dev|prod] [--update-backend-url]"
    exit 1
fi

ENVIRONMENT=$1
UPDATE_BACKEND_URL=$2

if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
    print_error "Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

echo "🚀 LegiSync Full Deployment - $ENVIRONMENT Environment"
echo "=============================================="

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

if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not installed. Install with: npm install -g @railway/cli"
fi

# Step 2: Deploy backend first (if Railway CLI is available)
if command -v railway &> /dev/null && [ "$UPDATE_BACKEND_URL" != "--update-backend-url" ]; then
    print_step "Deploying backend to Railway..."
    
    cd ../backend
    
    # Check if Railway project exists
    if railway status &> /dev/null; then
        print_status "Railway project found. Deploying..."
        railway up
        
        # Get the Railway URL
        RAILWAY_URL=$(railway status --json | jq -r '.deployment.url' 2>/dev/null || echo "")
        
        if [ -n "$RAILWAY_URL" ] && [ "$RAILWAY_URL" != "null" ]; then
            print_status "Backend deployed to: $RAILWAY_URL"
            
            # Update the backend URL in tfvars
            cd ../iac
            if [ "$ENVIRONMENT" == "dev" ]; then
                sed -i.bak "s|backend_url = \".*\"|backend_url = \"$RAILWAY_URL\"|" dev.tfvars
            else
                sed -i.bak "s|backend_url = \".*\"|backend_url = \"$RAILWAY_URL\"|" prod.tfvars  
            fi
            print_status "Updated backend URL in ${ENVIRONMENT}.tfvars"
        else
            print_warning "Could not get Railway URL automatically. You'll need to update manually."
        fi
    else
        print_warning "No Railway project found. Please run 'railway init' in the backend directory first."
        print_warning "Or deploy your backend manually and use --update-backend-url flag"
    fi
    
    cd ../iac
else
    print_warning "Skipping backend deployment. Make sure your backend is deployed separately."
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
    
    # Step 4: Data ingestion reminder
    echo
    print_step "Next Steps:"
    echo "1. ✅ Infrastructure deployed"
    echo "2. ✅ Frontend deployed to Vercel" 
    echo "3. ✅ Backend deployed to Railway"
    echo "4. 🔄 Run data ingestion:"
    echo "   cd ../backend"
    echo "   python ingest.py"
    echo "5. 🧪 Test your application:"
    echo "   Open: $FRONTEND_URL"
    
else
    print_warning "Deployment cancelled"
    rm -f "${ENVIRONMENT}.tfplan"
fi
