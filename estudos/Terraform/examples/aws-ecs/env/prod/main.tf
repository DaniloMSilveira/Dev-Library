module "prod" {
    source = "../../infra"

    repository = "production"
    repository_url = "962752222089.dkr.ecr.us-west-2.amazonaws.com"
    roleIAM = "production"
    environment = "production"
    ecs_container_cpu = 512
    ecs_container_memory = 1024
    ecs_container_count = 3
}

output "IP_alb" {
  value = module.prod.IP
}