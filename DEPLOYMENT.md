# LegiSync Deployment Guide

This guide will walk you through deploying LegiSync to production using Vercel (frontend) and Railway (backend).

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │  Pinecone   │
│  (Vercel)   │───▶│ (Railway)   │───▶│ (Vector DB) │
│  Next.js    │    │ FastAPI     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Prerequisites

- GitHub repository with your code
- Vercel account (free tier available)
- Railway account (free tier available)
- Pinecone account (free tier available)
- Domain name (optional)

## Step 1: Set Up API Keys

Gather the following API keys:

1. **Vercel API Token**: https://vercel.com/account/tokens
2. **Pinecone API Key**: https://app.pinecone.io/
3. **VoyageAI API Key**: https://dash.voyageai.com/
4. **LangChain API Key**: https://smith.langchain.com/ (optional, for tracing)
5. **Other AI API Keys**: OpenAI, Anthropic, Google (as needed)

## Step 2: Deploy Infrastructure with Terraform

```bash
# 1. Navigate to IaC directory
cd iac/

# 2. Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your API keys

# 3. Deploy to development
./deploy.sh dev

# 4. Deploy to production (when ready)
./deploy.sh prod
```

This will create:

- Vercel project
- Pinecone vector index
- Environment variables configuration

## Step 3: Deploy Backend to Railway

### Option A: Using Railway CLI

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Navigate to backend directory
cd ../backend/

# 4. Initialize Railway project
railway init

# 5. Set environment variables
railway variables set LANGCHAIN_TRACING_V2=true
railway variables set LANGCHAIN_API_KEY=your_key
railway variables set VOYAGE_API_KEY=your_key
railway variables set PINECONE_API_KEY=your_key
# ... set other API keys as needed

# 6. Deploy
railway up
```

### Option B: Using Railway Dashboard

1. Go to https://railway.app/
2. Create new project from GitHub
3. Select your repository
4. Choose the `backend/` folder as root
5. Set environment variables in the dashboard
6. Deploy

### Environment Variables for Backend

Set these in Railway dashboard:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_key
VOYAGE_API_KEY=your_voyage_key
PINECONE_API_KEY=your_pinecone_key
GOOGLE_API_KEY=your_google_key (optional)
ANTHROPIC_API_KEY=your_anthropic_key (optional)
OPENAI_API_KEY=your_openai_key (optional)
```

## Step 4: Update Frontend with Backend URL

After Railway deployment:

```bash
# 1. Get your Railway backend URL (e.g., https://backend-production-xxx.up.railway.app)
railway status

# 2. Update terraform variables
# Edit iac/dev.tfvars or iac/prod.tfvars:
backend_url = "https://your-backend-url.up.railway.app"

# 3. Re-deploy frontend
cd iac/
./deploy.sh dev  # or prod
```

## Step 5: Ingest Data

Once both frontend and backend are deployed:

```bash
# 1. Navigate to backend directory
cd backend/

# 2. Install dependencies locally (if not already done)
pip install -r requirements.txt

# 3. Set environment variables locally
export PINECONE_API_KEY=your_key
export VOYAGE_API_KEY=your_key

# 4. Run ingestion script
python ingest.py
```

## Step 6: Verify Deployment

1. **Frontend**: Visit your Vercel URL
2. **Backend**: Check https://your-backend-url.up.railway.app/health
3. **Integration**: Test the chat functionality

## Step 7: Custom Domain (Optional)

### For Frontend (Vercel):

1. Update `custom_domain` in your `.tfvars` file
2. Run `./deploy.sh prod`
3. Configure DNS records as shown in Vercel dashboard

### For Backend (Railway):

1. Go to Railway project settings
2. Add custom domain
3. Configure DNS records

## Monitoring and Maintenance

### Logs

- **Frontend**: Vercel dashboard → Functions tab
- **Backend**: Railway dashboard → Deployments tab
- **Pinecone**: Pinecone console → Usage tab

### Scaling

- **Frontend**: Automatically handled by Vercel
- **Backend**: Configure in Railway dashboard or `railway.toml`
- **Pinecone**: Serverless scales automatically

### Costs

- **Vercel**: Free tier covers most small projects
- **Railway**: $5/month after free trial
- **Pinecone**: Free tier includes 100k vectors

## Troubleshooting

### Common Issues

1. **CORS Errors**

   - Ensure frontend URL is in backend CORS origins
   - Check environment variable configuration

2. **Build Failures**

   - Check build logs in Vercel/Railway dashboards
   - Verify package.json dependencies

3. **API Connection Issues**

   - Verify backend URL in frontend environment
   - Check backend health endpoint
   - Confirm API keys are set correctly

4. **Pinecone Connection Issues**
   - Verify API key permissions
   - Check index name matches configuration
   - Ensure data has been ingested

### Getting Help

- **Vercel**: https://vercel.com/docs
- **Railway**: https://docs.railway.app/
- **Pinecone**: https://docs.pinecone.io/
- **Terraform**: https://terraform.io/docs

## Security Checklist

- [ ] API keys stored securely (not in code)
- [ ] CORS configured properly
- [ ] Environment variables set correctly
- [ ] terraform.tfvars not committed to git
- [ ] Production domain configured with HTTPS
- [ ] Regular key rotation scheduled

## Rollback Plan

If something goes wrong:

```bash
# Rollback infrastructure
cd iac/
terraform destroy -var-file="prod.tfvars"

# Redeploy previous version
git checkout <previous-commit>
./deploy.sh prod
```

## Next Steps

After successful deployment:

1. Set up monitoring/alerting
2. Configure backup strategy
3. Set up CI/CD pipeline
4. Plan for scaling
5. Security audit
