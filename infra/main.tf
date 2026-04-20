terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.95"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  default_tags = {
    Project   = var.name
    ManagedBy = "terraform"
  }

  tags = merge(local.default_tags, var.tags)
}

module "ecr" {
  source = "./modules/ecr"

  repository_name       = "${var.name}-api"
  force_delete          = var.ecr_force_delete
  image_retention_count = 10
  tags                  = local.tags
}

module "apprunner" {
  source = "./modules/apprunner"

  service_name       = "${var.name}-api"
  ecr_repository_url = module.ecr.repository_url
  image_tag          = var.image_tag
  use_image_digest   = var.use_image_digest
  container_port     = var.container_port
  cpu                = var.apprunner_cpu
  memory             = var.apprunner_memory
  sessions_dir_path  = var.sessions_dir_path
  tags               = local.tags
}

module "apigateway" {
  source = "./modules/apigateway"

  name                    = "${var.name}-rest"
  aws_region              = var.aws_region
  backend_url             = module.apprunner.service_url
  stage_name              = var.api_stage_name
  api_key_value           = var.api_key_value
  usage_plan_rate_limit   = var.usage_plan_rate_limit
  usage_plan_burst_limit  = var.usage_plan_burst_limit
  usage_plan_quota_limit  = var.usage_plan_quota_limit
  usage_plan_quota_period = var.usage_plan_quota_period
  tags                    = local.tags
}
