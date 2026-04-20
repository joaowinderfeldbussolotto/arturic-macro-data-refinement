locals {
  ecr_repository_name = element(reverse(split("/", var.ecr_repository_url)), 0)

  app_image_identifier = var.use_image_digest ? "${var.ecr_repository_url}@${data.aws_ecr_image.selected[0].image_digest}" : "${var.ecr_repository_url}:${var.image_tag}"
}

data "aws_ecr_image" "selected" {
  count = var.use_image_digest ? 1 : 0

  repository_name = local.ecr_repository_name
  image_tag       = var.image_tag
}

resource "aws_iam_role" "ecr_access" {
  name = "${var.service_name}-ecr-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecr_access" {
  role       = aws_iam_role.ecr_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

resource "aws_iam_role" "instance" {
  name = "${var.service_name}-instance"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_apprunner_service" "this" {
  service_name = var.service_name

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.ecr_access.arn
    }

    image_repository {
      image_repository_type = "ECR"
      image_identifier      = local.app_image_identifier

      image_configuration {
        port = tostring(var.container_port)

        runtime_environment_variables = {
          SESSIONS_DIR = var.sessions_dir_path
        }
      }
    }
  }

  instance_configuration {
    cpu               = var.cpu
    memory            = var.memory
    instance_role_arn = aws_iam_role.instance.arn
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/api/v1/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  tags = var.tags

  depends_on = [aws_iam_role_policy_attachment.ecr_access]
}
