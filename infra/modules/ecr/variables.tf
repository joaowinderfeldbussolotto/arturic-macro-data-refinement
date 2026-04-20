variable "repository_name" {
  description = "ECR repository name."
  type        = string
}

variable "force_delete" {
  description = "When true, deleting repository will also remove all images."
  type        = bool
  default     = true
}

variable "image_retention_count" {
  description = "How many recent images to keep in ECR."
  type        = number
  default     = 10
}

variable "tags" {
  description = "Tags applied to ECR resources."
  type        = map(string)
  default     = {}
}
