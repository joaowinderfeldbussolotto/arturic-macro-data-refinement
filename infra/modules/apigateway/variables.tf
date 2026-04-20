variable "name" {
  description = "Base name used in API Gateway resources."
  type        = string
}

variable "aws_region" {
  description = "AWS region where API Gateway is created."
  type        = string
}

variable "backend_url" {
  description = "Public backend URL used by API Gateway HTTP_PROXY integration."
  type        = string
}

variable "stage_name" {
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
  description = "Steady-state request rate limit."
  type        = number
  default     = 100
}

variable "usage_plan_burst_limit" {
  description = "Burst request limit."
  type        = number
  default     = 200
}

variable "usage_plan_quota_limit" {
  description = "Quota limit for API key usage plan."
  type        = number
  default     = 100000
}

variable "usage_plan_quota_period" {
  description = "Quota period (DAY, WEEK, MONTH)."
  type        = string
  default     = "MONTH"

  validation {
    condition     = contains(["DAY", "WEEK", "MONTH"], var.usage_plan_quota_period)
    error_message = "usage_plan_quota_period must be DAY, WEEK, or MONTH."
  }
}

variable "tags" {
  description = "Tags applied to API Gateway resources."
  type        = map(string)
  default     = {}
}
