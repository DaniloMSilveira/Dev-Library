variable "environment" {
    type = string
}
variable "aws_region" {
    type = string
}
variable "ssh_key" {
  type = string
}
variable "instance_type" {
  type = string
}
variable "security_group" {
  type = string
}
variable "asg_name" {
  type = string
}
variable "asg_max_size" {
  type = number
}
variable "asg_min_size" {
  type = number
}
variable "is_production" {
  type = bool
}