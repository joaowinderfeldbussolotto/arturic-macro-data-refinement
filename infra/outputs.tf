output "ecr_repository_url" {
  description = "ECR repository URL."
  value       = module.ecr.repository_url
}

output "app_runner_service_url" {
  description = "Public URL of App Runner service."
  value       = module.apprunner.service_url
}

output "api_gateway_base_url" {
  description = "Base URL of API Gateway stage."
  value       = module.apigateway.base_url
}

output "api_gateway_healthcheck_url" {
  description = "Health endpoint URL exposed by API Gateway."
  value       = module.apigateway.healthcheck_url
}

output "api_key" {
  description = "API key required in x-api-key header."
  value       = module.apigateway.api_key
  sensitive   = true
}

output "docker_login_command" {
  description = "Command to authenticate Docker in ECR."
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${module.ecr.registry_host}"
}

output "docker_build_command" {
  description = "Command to build local API image from repository root."
  value       = "docker build -t ${var.name}-api:${var.image_tag} -f ../Dockerfile .."
}

output "docker_tag_command" {
  description = "Command to tag local image with ECR repository URL."
  value       = "docker tag ${var.name}-api:${var.image_tag} ${module.ecr.repository_url}:${var.image_tag}"
}

output "docker_push_command" {
  description = "Command to push image to ECR."
  value       = "docker push ${module.ecr.repository_url}:${var.image_tag}"
}

output "docker_push_commands" {
  description = "All commands needed to push image to ECR before full apply."
  value       = <<-EOT
  aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${module.ecr.registry_host}
  docker build -t ${var.name}-api:${var.image_tag} -f ../Dockerfile ..
  docker tag ${var.name}-api:${var.image_tag} ${module.ecr.repository_url}:${var.image_tag}
  docker push ${module.ecr.repository_url}:${var.image_tag}
  EOT
}
