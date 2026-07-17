module "aws-dev" {
  source = "../../infra"
  environment = "DEV"
  aws_region = "us-west-2"
  instance_type = "t2.micro"
  ssh_key = "iac-dev"
  security_group = "full-access-dev"
  asg_name = "asg-dev"
  asg_min_size = 0
  asg_max_size = 1
  is_production = false
}