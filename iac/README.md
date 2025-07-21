# LegiSync Infrastructure as Code

This directory contains Terraform configuration for deploying the LegiSync application to Vercel with Pinecone vector database infrastructure.

## Architecture

- **Frontend**: Next.js application deployed to Vercel
- **Vector Database**: Pinecone serverless index for bill embeddings
- **Backend**: Python FastAPI (deploy separately to Railway/Render/etc.)

## Prerequisites

1. **Terraform**: Install Terraform >= 1.0

   ```bash
   brew install terraform  # macOS
   # or download from https://terraform.io/downloads
   ```

2. **Vercel Account**:

   - Sign up at https://vercel.com
   - Generate API token at https://vercel.com/account/tokens

3. **Pinecone Account**:

   - Sign up at https://pinecone.io
   - Get API key from dashboard

4. **GitHub Repository**: Ensure your code is pushed to GitHub

## Setup

### 1. Configure API Tokens

Copy the example variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your actual values:

```hcl
vercel_api_token = "your_vercel_token"
pinecone_api_key = "your_pinecone_key"
# ... other API keys
```

**⚠️ Never commit terraform.tfvars to version control!**

### 2. Initialize Terraform

```bash
cd iac/
terraform init
```

### 3. Review Planned Changes

For development:

```bash
terraform plan -var-file="dev.tfvars"
```

For production:

```bash
terraform plan -var-file="prod.tfvars"
```

### 4. Deploy Infrastructure

For development:

```bash
terraform apply -var-file="dev.tfvars"
```

For production:

```bash
terraform apply -var-file="prod.tfvars"
```

## Deployment Environments

### Development (`dev.tfvars`)

- Vercel project: `legisync-dev`
- Pinecone index: `bills-index-dev`
- URL: `https://legisync-dev.vercel.app`

### Production (`prod.tfvars`)

- Vercel project: `legisync-prod`
- Pinecone index: `bills-index-prod`
- Custom domain support
- URL: `https://legisync-prod.vercel.app` (or custom domain)

## Post-Deployment Steps

### 1. Deploy Backend

The Terraform only handles frontend (Vercel) and vector database (Pinecone). Deploy your FastAPI backend separately:

**Railway:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

**Render:**

1. Connect GitHub repository
2. Set build/start commands
3. Add environment variables

### 2. Update Backend URL

After deploying your backend, update the `backend_url` in your `.tfvars` file and re-run:

```bash
terraform apply -var-file="dev.tfvars"
```

### 3. Ingest Data

Run your data ingestion script against the new Pinecone index:

```bash
cd ../backend
python ingest.py
```

## Managing Secrets

### Option 1: Environment Variables

```bash
export TF_VAR_vercel_api_token="your_token"
export TF_VAR_pinecone_api_key="your_key"
terraform apply -var-file="dev.tfvars"
```

### Option 2: Terraform Cloud (Recommended for Production)

1. Create workspace at https://app.terraform.io
2. Set variables as "Environment Variables" with "Sensitive" flag
3. Connect to your GitHub repository

## Common Commands

```bash
# View current state
terraform show

# View outputs
terraform output

# Destroy infrastructure (careful!)
terraform destroy -var-file="dev.tfvars"

# Format configuration files
terraform fmt

# Validate configuration
terraform validate
```

## Troubleshooting

### Vercel Deployment Issues

- Check build logs in Vercel dashboard
- Verify `build_command` and `output_directory` paths
- Ensure environment variables are set correctly

### Pinecone Issues

- Verify API key permissions
- Check index name doesn't already exist
- Ensure dimension matches your embedding model (1024 for VoyageAI)

### Backend Connection Issues

- Verify `BACKEND_URL` environment variable in Vercel
- Check CORS settings in FastAPI backend
- Ensure backend is deployed and accessible

## Security Notes

1. **Never commit sensitive files:**

   - `terraform.tfvars`
   - `*.tfstate`
   - `.env` files

2. **Use least-privilege API keys**
3. **Rotate keys regularly**
4. **Enable MFA on cloud accounts**

## File Structure

```
iac/
├── main.tf              # Main infrastructure resources
├── variables.tf         # Variable definitions
├── outputs.tf          # Output values
├── dev.tfvars          # Development environment config
├── prod.tfvars         # Production environment config
├── terraform.tfvars.example  # Template for secrets
├── .gitignore          # Ignore sensitive files
└── README.md           # This file
```

## Support

For issues with:

- **Terraform**: Check the Terraform documentation
- **Vercel**: Check Vercel dashboard and docs
- **Pinecone**: Check Pinecone console and docs
- **This setup**: Open an issue in the repository
