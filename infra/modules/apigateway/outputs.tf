output "rest_api_id" {
  description = "API Gateway REST API ID."
  value       = aws_api_gateway_rest_api.this.id
}

output "stage_name" {
  description = "API Gateway stage name."
  value       = aws_api_gateway_stage.this.stage_name
}

output "base_url" {
  description = "API Gateway base URL for this stage."
  value       = "https://${aws_api_gateway_rest_api.this.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.this.stage_name}"
}

output "healthcheck_url" {
  description = "Health endpoint proxied via API Gateway."
  value       = "https://${aws_api_gateway_rest_api.this.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.this.stage_name}/api/v1/health"
}

output "api_key" {
  description = "API key used by clients in x-api-key header."
  value       = aws_api_gateway_api_key.client.value
  sensitive   = true
}
