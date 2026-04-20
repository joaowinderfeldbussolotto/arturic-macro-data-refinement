variable "service_name" {
  description = "App Runner service name."
  type        = string
}

variable "ecr_repository_url" {
  description = "ECR repository URL where the API image is stored."
  type        = string
}

variable "image_tag" {
  description = "Image tag pulled by App Runner."
  type        = string
}

variable "use_image_digest" {
  description = "When true, resolves image digest from ECR and pins App Runner deployment."
  type        = bool
  default     = true
}

variable "container_port" {
  description = "Container port exposed by the API image."
  type        = number
  default     = 8000
}

variable "cpu" {
  description = "App Runner CPU units."
  type        = string
  default     = "1024"
}

variable "memory" {
  description = "App Runner memory in MB."
  type        = string
  default     = "2048"
}

variable "sessions_dir_path" {
  description = "Path inside container where session data is available."
  type        = string
  default     = "/app/data"
}

variable "tags" {
  description = "Tags applied to App Runner and IAM resources."
  type        = map(string)
  default     = {}
}
