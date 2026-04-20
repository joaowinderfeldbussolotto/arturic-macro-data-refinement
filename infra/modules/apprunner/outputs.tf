output "service_arn" {
  description = "App Runner service ARN."
  value       = aws_apprunner_service.this.arn
}

output "service_id" {
  description = "App Runner service ID."
  value       = aws_apprunner_service.this.service_id
}

output "service_url" {
  description = "App Runner public URL."
  value       = can(regex("^https?://", aws_apprunner_service.this.service_url)) ? aws_apprunner_service.this.service_url : "https://${aws_apprunner_service.this.service_url}"
}

output "ecr_access_role_arn" {
  description = "IAM role ARN used by App Runner to pull ECR images."
  value       = aws_iam_role.ecr_access.arn
}

output "instance_role_arn" {
  description = "IAM role ARN attached to App Runner instances."
  value       = aws_iam_role.instance.arn
}
