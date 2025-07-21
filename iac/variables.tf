# Core Configuration Variables
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "github_repo" {
  description = "GitHub repository in format 'owner/repo'"
  type        = string
  default     = "ccfegenbush/legisync"
}

# Vercel Configuration
variable "vercel_api_token" {
  description = "Vercel API token for authentication"
  type        = string
  sensitive   = true
}

variable "custom_domain" {
  description = "Custom domain for the application (optional)"
  type        = string
  default     = ""
}

variable "backend_url" {
  description = "Backend API URL for the frontend to connect to"
  type        = string
  default     = "https://your-backend-url.com"
}

# Pinecone Configuration
variable "pinecone_api_key" {
  description = "Pinecone API key for vector database"
  type        = string
  sensitive   = true
}

variable "pinecone_index_name" {
  description = "Name of the Pinecone index"
  type        = string
  default     = "bills-index"
}

# API Keys for Backend (stored in Vercel environment variables)
variable "langchain_api_key" {
  description = "LangChain API key for tracing"
  type        = string
  sensitive   = true
  default     = ""
}

variable "voyage_api_key" {
  description = "Voyage AI API key for embeddings"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_api_key" {
  description = "Google API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}
