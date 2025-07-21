# LegiSync Deployment Guide

This guide will walk you through deploying LegiSync to prod```bash

# 1. Get your Render backend URL (e.g., https://legisync-backend-prod.onrender.com)

# Check your Render dashboard for the URL

# 2. Update terraform variables

# Edit iac/dev.tfvars or iac/prod.tfvars:

backend_url = "https://your-render-url.onrender.com"using Vercel (frontend) and Render (backend).

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │  Pinecone   │
│  (Vercel)   │───▶│  (Render)   │───▶│ (Vector DB) │
│  Next.js    │    │ FastAPI     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Prerequisites

- GitHub repository with your code
- Vercel account (free tier available)
- Render account (free tier available)
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

## Step 3: Deploy Backend to Render

### Deploy via Render Dashboard

1. Go to https://dashboard.render.com/
2. Click "New" > "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `legisync-backend-prod` (or `legisync-backend-dev`)
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Set environment variables in the dashboard (see below)
6. Click "Deploy"

### Environment Variables for Backend

Set these in the Render dashboard under "Environment":

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

After Render deployment:

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
2. **Backend**: Check https://your-backend-url.onrender.com/health
3. **Integration**: Test the chat functionality

## Step 7: Custom Domain (Optional)

### For Frontend (Vercel):

1. Update `custom_domain` in your `.tfvars` file
2. Run `./deploy.sh prod`
3. Configure DNS records as shown in Vercel dashboard

### For Backend (Render):

1. Go to Render dashboard > Service settings
2. Add custom domain
3. Configure DNS records as shown in Render

## Monitoring and Maintenance

### Logs

- **Frontend**: Vercel dashboard → Functions tab
- **Backend**: Render dashboard → Logs tab
- **Pinecone**: Pinecone console → Usage tab

### Scaling

- **Frontend**: Automatically handled by Vercel
- **Backend**: Configure scaling in Render dashboard
- **Pinecone**: Serverless scales automatically

### Costs

- **Vercel**: Free tier covers most small projects
- **Render**: Free tier available, $7/month for production
- **Pinecone**: Free tier includes 100k vectors

## Troubleshooting

### Common Issues

1. **CORS Errors**

   - Ensure frontend URL is in backend CORS origins
   - Check environment variable configuration

2. **Build Failures**

   - Check build logs in Vercel/Render dashboards
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
- **Render**: https://render.com/docs
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
