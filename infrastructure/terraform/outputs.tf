output "alb_dns_name" {
  description = "Application Load Balancer DNS — access the app at http://<alb_dns_name>"
  value       = aws_lb.main.dns_name
}

output "backend_ecr_uri" {
  description = "ECR URI for pushing backend images"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_ecr_uri" {
  description = "ECR URI for pushing frontend images"
  value       = aws_ecr_repository.frontend.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "vpc_id" {
  value = aws_vpc.main.id
}
