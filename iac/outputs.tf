# Vercel Project Outputs
output "vercel_project_id" {
  description = "The ID of the created Vercel project"
  value       = vercel_project.legisync_frontend.id
}

output "vercel_project_name" {
  description = "The name of the created Vercel project"
  value       = vercel_project.legisync_frontend.name
}

output "vercel_deployment_url" {
  description = "The production URL of the Vercel deployment"
  value       = "https://${vercel_project.legisync_frontend.name}.vercel.app"
}

output "vercel_custom_domain" {
  description = "The custom domain (if configured)"
  value       = var.custom_domain != "" ? var.custom_domain : null
}

# Pinecone Outputs
output "pinecone_index_name" {
  description = "The name of the created Pinecone index"
  value       = pinecone_index.bills_index.name
}

output "pinecone_index_host" {
  description = "The host URL of the Pinecone index"
  value       = pinecone_index.bills_index.host
  sensitive   = true
}

output "pinecone_index_dimension" {
  description = "The dimension of the Pinecone index"
  value       = pinecone_index.bills_index.dimension
}

# Deployment Information
output "deployment_info" {
  description = "Summary of deployment information"
  value = {
    environment     = var.environment
    frontend_url    = "https://${vercel_project.legisync_frontend.name}.vercel.app"
    custom_domain   = var.custom_domain != "" ? var.custom_domain : "none"
    pinecone_index  = pinecone_index.bills_index.name
    backend_url     = var.backend_url
  }
}
