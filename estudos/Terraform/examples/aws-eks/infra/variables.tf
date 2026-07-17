variable "repository_url" {
  type = string
}

variable "repository" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "replicas" {
  type = number
}

variable "cpu_limit" {
  type = string
}

variable "memory_limit" {
  type = string
}

variable "cpu_request" {
  type = string
}

variable "memory_request" {
  type = string
}