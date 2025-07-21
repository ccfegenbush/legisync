# LegiSync Backend Deployment Options

## 🏆 Recommended: Render

**Best overall choice for your FastAPI backend**

### Why Render?

- ✅ **Free tier**: 750 hours/month free
- ✅ **Zero config**: Just connect GitHub and deploy
- ✅ **Auto HTTPS**: SSL certificates included
- ✅ **Environment variables**: Easy secret management
- ✅ **Health checks**: Built-in monitoring
- ✅ **Custom domains**: Free SSL for custom domains
- ✅ **Git integration**: Auto-deploy on push

### Setup Steps:

1. Go to https://dashboard.render.com/
2. Click "New" > "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: `legisync-backend-prod`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard
6. Deploy!

**Your URL**: `https://legisync-backend-prod.onrender.com`

---

## ☁️ Alternative: Google Cloud Run

**Best for high scale, serverless pricing**

### Setup:

```bash
# Install gcloud CLI
gcloud auth login
gcloud run deploy legisync-backend --source . --platform managed
```

**Cost**: Pay per request (practically free for low traffic)

---

## 🐳 Alternative: Fly.io

**Best performance, Docker-based**

### Setup:

```bash
# Install flyctl
brew install flyctl
flyctl auth login
flyctl init
flyctl deploy
```

**Cost**: $1.94/month for minimal resources

---

## 💡 Alternative: AWS Lambda

**Cheapest option for low traffic**

### Setup:

Use AWS SAM or Serverless Framework to deploy FastAPI as Lambda functions.

**Cost**: Free tier covers most small apps

---

## 🎯 My Recommendation

For **LegiSync**, I recommend **Render** because:

1. **Free tier**: Perfect for development/testing
2. **Simple setup**: Just connect GitHub
3. **Automatic deployments**: Deploy on git push
4. **Built-in SSL**: HTTPS out of the box
5. **Environment variables**: Easy secret management
6. **Health checks**: Monitors your `/health` endpoint
7. **Scaling**: Can handle production traffic
8. **Custom domains**: Add your own domain for free

## 🚀 Quick Start with Render

1. **Push your code to GitHub** (if not already)
2. **Go to Render dashboard**: https://dashboard.render.com/
3. **Create Web Service** from your GitHub repo
4. **Set environment variables** in Render dashboard
5. **Deploy automatically**!

Your backend will be live at: `https://your-service-name.onrender.com`

Then update your `terraform.tfvars`:

```hcl
backend_url = "https://legisync-backend-prod.onrender.com"
```

**No CLI tools needed, just a web interface!** 🎉
