variable "repository" {
  type = string
}

variable "repository_url" {
  type = string
}

variable "roleIAM" {
  type = string
}

variable "environment" {
  type = string
}

variable ecs_container_cpu {
  type = number
}

variable ecs_container_memory {
  type = number
}

variable ecs_container_count {
  type = number
}