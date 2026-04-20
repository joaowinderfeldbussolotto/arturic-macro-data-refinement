variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "name" {
  description = "Base name used in AWS resources."
  type        = string
  default     = "arturic-macro-data-refinement"
}

variable "image_tag" {
  description = "Image tag that App Runner will pull from ECR."
  type        = string
  default     = "latest"
}

variable "use_image_digest" {
  description = "When true, App Runner pins to digest resolved from ECR for image_tag."
  type        = bool
  default     = true
}

variable "ecr_force_delete" {
  description = "When true, Terraform can delete ECR repository even if it still contains images."
  type        = bool
  default     = true
}

variable "apprunner_cpu" {
  description = "App Runner CPU units (example: 1024, 2048)."
  type        = string
  default     = "1024"
}

variable "apprunner_memory" {
  description = "App Runner memory in MB (example: 2048, 3072, 4096)."
  type        = string
  default     = "2048"
}

variable "container_port" {
  description = "Port exposed by the container image."
  type        = number
  default     = 8000
}

variable "sessions_dir_path" {
  description = "Path inside the container where data files are available."
  type        = string
  default     = "/app/data"
}

variable "api_stage_name" {
  description = "API Gateway stage name."
  type        = string
  default     = "prod"
}

variable "api_key_value" {
  description = "Optional fixed API key. If null/empty, one is generated."
  type        = string
  default     = null
  sensitive   = true
}

variable "usage_plan_rate_limit" {
  description = "Steady-state request rate limit for API key usage plan."
  type        = number
  default     = 100
}

variable "usage_plan_burst_limit" {
  description = "Burst request limit for API key usage plan."
  type        = number
  default     = 200
}

variable "usage_plan_quota_limit" {
  description = "Quota limit for API key usage plan."
  type        = number
  default     = 100000
}

variable "usage_plan_quota_period" {
  description = "Quota period for usage plan (DAY, WEEK, MONTH)."
  type        = string
  default     = "MONTH"

  validation {
    condition     = contains(["DAY", "WEEK", "MONTH"], var.usage_plan_quota_period)
    error_message = "usage_plan_quota_period must be DAY, WEEK, or MONTH."
  }
}

variable "tags" {
  description = "Additional tags for AWS resources."
  type        = map(string)
  default     = {}
}
