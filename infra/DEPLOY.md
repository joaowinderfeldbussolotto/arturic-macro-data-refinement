# AWS Deploy (Terraform Modules)

This directory uses a modular Terraform layout:

- modules/ecr
- modules/apprunner
- modules/apigateway

Because App Runner needs an image that already exists in ECR, deploy is done in two phases.

## 1) Export AWS credentials (required in this environment)

```bash
eval "$(aws configure export-credentials --profile default --format env)"
```

## 2) Create ECR first

```bash
cd infra
terraform init
cp terraform.tfvars.example terraform.tfvars
terraform apply -target=module.ecr
```

## 3) Build and push the API image to ECR

Get generated commands:

```bash
terraform output -raw docker_push_commands
```

Run them (from infra directory):

```bash
# copy and run the generated lines from the previous command output
```

## 4) Apply full stack

```bash
terraform apply
```

## 5) Read outputs

```bash
terraform output api_gateway_base_url
terraform output api_gateway_healthcheck_url
terraform output -raw api_key
```

## 6) Test with API key

```bash
curl -sS "$(terraform output -raw api_gateway_healthcheck_url)" \
  -H "x-api-key: $(terraform output -raw api_key)"
```

Expected response:

```json
{"status":"ok"}
```

## Notes

- If the API Gateway returns 403 right after apply, wait 1-2 minutes and retry. API key associations can take a short time to propagate.
- If App Runner had a previous failed deploy and Terraform reports replacement/name conflict, run:

  terraform untaint module.apprunner.aws_apprunner_service.this

  Then run terraform apply again.
- ECR repository uses force delete by default (`ecr_force_delete = true`), so `terraform destroy` can remove it even with images.
- If image/tag was manually removed and destroy fails on ECR digest lookup, run:

  terraform destroy -var='use_image_digest=false'
