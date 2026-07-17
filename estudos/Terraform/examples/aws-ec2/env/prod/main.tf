module "aws-prod" {
  source = "../../infra"
  environment = "PROD"
  aws_region = "us-west-2"
  instance_type = "t2.micro"
  ssh_key = "iac-prod"
  security_group = "full-access-prod"
  asg_name = "asg-prod"
  asg_min_size = 1
  asg_max_size = 5
  is_production = true
}