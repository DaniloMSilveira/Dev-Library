module "prod" {
    source = "../../infra"

    repository = "development"
    repository_url = "962752222089.dkr.ecr.us-west-2.amazonaws.com"
    roleIAM = "development"
    environment = "development"
    ecs_container_cpu = 256
    ecs_container_memory = 512
    ecs_container_count = 1
}

output "IP_alb" {
  value = module.prod.IP
}