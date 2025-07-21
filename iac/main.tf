terraform {
  required_version = ">= 1.0"
  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 2.0"
    }
    pinecone = {
      source  = "pinecone-io/pinecone"
      version = "~> 0.7"
    }
  }
}

# Configure providers
provider "vercel" {
  api_token = var.vercel_api_token
}

provider "pinecone" {
  api_key = var.pinecone_api_key
}

# Create Pinecone index for bill embeddings
resource "pinecone_index" "bills_index" {
  name      = var.pinecone_index_name
  dimension = 1024  # VoyageAI embedding dimension
  metric    = "cosine"
  
  spec = {
    serverless = {
      cloud  = "aws"
      region = "us-east-1"
    }
  }

  tags = {
    Environment = var.environment
    Project     = "legisync"
    ManagedBy   = "terraform"
  }
}

# Create Vercel project
resource "vercel_project" "legisync_frontend" {
  name      = "legisync-${var.environment}"
  framework = "nextjs"

  git_repository = {
    type = "github"
    repo = var.github_repo
  }

  # Build settings for Next.js in pnpm workspace
  build_command    = "pnpm build"
  dev_command      = "pnpm dev" 
  install_command  = "cd .. && pnpm install && cd frontend"
  output_directory = ".next"
  root_directory   = "frontend"

  # Environment variables for the frontend
  environment = [
    {
      key    = "BACKEND_URL"
      value  = var.backend_url
      target = ["production", "preview", "development"]
    },
    {
      key    = "NEXT_PUBLIC_APP_ENV"
      value  = var.environment
      target = ["production", "preview", "development"]
    }
  ]

  # Auto-assign domains
  auto_assign_custom_domains = true

  tags = {
    Environment = var.environment
    Project     = "legisync"
    ManagedBy   = "terraform"
  }
}

# Custom domain (optional)
resource "vercel_project_domain" "legisync_domain" {
  count      = var.custom_domain != "" ? 1 : 0
  project_id = vercel_project.legisync_frontend.id
  domain     = var.custom_domain
}