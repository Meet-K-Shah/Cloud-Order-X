terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — update bucket/key for your environment
  backend "s3" {
    bucket  = "cloudorderx-tfstate"
    key     = "cloudorderx/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CloudOrderX"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
