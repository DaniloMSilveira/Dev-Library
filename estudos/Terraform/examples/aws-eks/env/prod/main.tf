module "prod" {
    source = "../../infra"

    repository_url = "962752222089.dkr.ecr.us-west-2.amazonaws.com"
    repository = "production"
    cluster_name = "production"
    replicas = 3
    cpu_limit = "500m"
    memory_limit = "512Mi"
    cpu_request = "250m"
    memory_request = "256Mi"
}

output "lb_url" {
    value = module.prod.URL
}