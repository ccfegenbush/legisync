# LegiSync

A modern RAG (Retrieval-Augmented Generation) application for querying Texas legislative bills using AI-powered search and analysis.

## Architecture

- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Backend**: FastAPI with LangChain and RAG pipeline
- **Vector Database**: Pinecone for bill embeddings
- **Embeddings**: VoyageAI for high-quality text embeddings
- **Deployment**: Vercel (frontend) + Railway (backend)

## Features

- 🔍 **Semantic Search**: Query Texas bills using natural language
- 🤖 **AI-Powered Analysis**: Get intelligent summaries and insights
- ⚡ **Fast Vector Search**: Powered by Pinecone serverless
- 🧪 **Comprehensive Testing**: Unit, integration, and e2e tests
- 🚀 **Production Ready**: Infrastructure as Code with Terraform

## Quick Start

### Development

```bash
# Clone repository
git clone https://github.com/ccfegenbush/legisync.git
cd legisync

# Install dependencies
pnpm install

# Start backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload

# Start frontend (new terminal)
cd frontend
pnpm dev

# Open http://localhost:3000
```

### Testing

```bash
# Frontend tests
cd frontend
pnpm test

# Backend tests
cd backend
pytest

# E2E tests
cd frontend
pnpm e2e
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production deployment guide.

### Quick Deploy

```bash
# Set up infrastructure
cd iac/
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your API keys
./deploy.sh prod

# Deploy backend to Railway
cd ../backend/
railway up

# Update frontend with backend URL
cd ../iac/
# Edit prod.tfvars with Railway URL
./deploy.sh prod
```

## Project Structure

```
legisync/
├── frontend/           # Next.js frontend
├── backend/           # FastAPI backend
├── iac/              # Terraform infrastructure
├── .github/          # GitHub Actions CI/CD
├── DEPLOYMENT.md     # Deployment guide
└── README.md         # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
