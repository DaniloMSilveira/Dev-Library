module "ecs" {
  source = "terraform-aws-modules/ecs/aws"

  name               = var.environment
  container_insights = true
  capacity_providers = ["FARGATE"]
  default_capacity_provider_strategy = [
    {
      capacity_provider = "FARGATE"
    }
  ]
}

resource "aws_ecs_task_definition" "app_task_definition" {
  family                   = "app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ecs_container_cpu
  memory                   = var.ecs_container_memory
  execution_role_arn       = aws_iam_role.role.arn
  container_definitions = jsonencode(
    [
      {
        "name"      = "${var.environment}"
        "image"     = "${var.repository_url}/${var.environment}:v1"
        "cpu"       = var.ecs_container_cpu
        "memory"    = var.ecs_container_memory
        "essential" = true
        "portMappings" = [
          {
            "containerPort" = 8000
            "hostPort"      = 8000
          }
        ]
      }
    ]
  )
}


resource "aws_ecs_service" "app_service" {
  name            = "app"
  cluster         = module.ecs.ecs_cluster_id
  task_definition = aws_ecs_task_definition.app_task_definition.arn
  desired_count   = var.ecs_container_count

  load_balancer {
    target_group_arn = aws_lb_target_group.target.arn
    container_name   = var.environment
    container_port   = 8000
  }

  network_configuration {
      subnets = module.vpc.private_subnets
      security_groups = [aws_security_group.private_security_group.id]
  }

  capacity_provider_strategy {
      capacity_provider = "FARGATE"
      weight = 1 #100/100
  }
}