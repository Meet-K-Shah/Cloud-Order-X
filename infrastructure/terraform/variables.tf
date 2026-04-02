# ── General ────────────────────────────────────────────────────────────────────
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev | staging | prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Prefix used in all resource names"
  type        = string
  default     = "cloudorderx"
}

# ── Networking ─────────────────────────────────────────────────────────────────
variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.11.0/24", "10.0.12.0/24"]
}

# ── Compute ────────────────────────────────────────────────────────────────────
variable "backend_instance_type" {
  default = "t3.medium"
}

variable "backend_desired_count" {
  description = "Desired ECS task count for backend"
  type        = number
  default     = 2
}

variable "backend_min_count" {
  type    = number
  default = 1
}

variable "backend_max_count" {
  type    = number
  default = 6
}

# ── Database ───────────────────────────────────────────────────────────────────
variable "db_instance_class" {
  default = "db.t3.micro"
}

variable "db_name" {
  default = "cloudorderx"
}

variable "db_username" {
  default   = "cloudorderx"
  sensitive = true
}

variable "db_password" {
  description = "RDS master password — set via TF_VAR_db_password"
  type        = string
  sensitive   = true
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS (recommended for prod)"
  type        = bool
  default     = false
}

# ── Container Images ───────────────────────────────────────────────────────────
variable "backend_image" {
  description = "ECR image URI for Spring Boot backend"
  default     = "cloudorderx/backend:latest"
}

variable "frontend_image" {
  description = "ECR image URI for Angular frontend"
  default     = "cloudorderx/frontend:latest"
}
