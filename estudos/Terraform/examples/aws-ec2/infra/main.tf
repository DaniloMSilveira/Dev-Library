provider "aws" {
  region = var.aws_region
}

resource "aws_launch_template" "app_server" {
  image_id = "ami-0786adace1541ca80"
  instance_type = var.instance_type
  key_name = var.ssh_key
  tags = {
    Name = "Terraform Server Python - ${var.environment}"
  }
  security_group_names = [ var.security_group ]
  user_data = var.is_production ? ("ansible.sh") : ""
}

resource "aws_key_pair" "app_server_keypair" {
  key_name   = var.ssh_key
  public_key = file("${var.ssh_key}.pub")
}

resource "aws_autoscaling_group" "app_server_asg" {
  name = var.asg_name
  max_size = var.asg_max_size
  min_size = var.asg_min_size
  desired_capacity = 1
  launch_template {
    id = aws_launch_template.app_server.id
    version = "$Latest"
  }
  availability_zones = [ "${var.aws_region}a", "${var.aws_region}b" ]
  target_group_arns = var.is_production ? [ aws_lb_target_group.app_server_lb_target_group[0].arn ] : []
}

resource "aws_autoscaling_schedule" "app_server_asg_scale_up" {
  scheduled_action_name = "app_server_asg_scale_up"
  autoscaling_group_name = aws_autoscaling_group.app_server_asg.name
  min_size = 0
  max_size = 1
  desired_capacity = 1
  start_time = timeadd(timestamp(), "10m")
  recurrence = "0 10 * * MON-FRI"
}

resource "aws_autoscaling_schedule" "app_server_asg_scale_down" {
  scheduled_action_name = "app_server_asg_scale_down"
  autoscaling_group_name = aws_autoscaling_group.app_server_asg.name
  min_size = 0
  max_size = 1
  desired_capacity = 0
  start_time = timeadd(timestamp(), "11m")
  recurrence = "0 21 * * MON-FRI"
}

resource "aws_default_subnet" "subnet_1" {
  availability_zone = "${var.aws_region}a"
}

resource "aws_default_subnet" "subnet_2" {
  availability_zone = "${var.aws_region}b"
}

resource "aws_lb" "app_server_lb" {
  internal = false
  subnets = [ aws_default_subnet.subnet_1.id, aws_default_subnet.subnet_2.id ]
  count = var.is_production ? 1 : 0
}

resource "aws_default_vpc" "vpc_default" {

}

resource "aws_lb_target_group" "app_server_lb_target_group" {
  name = "app-server-lb-tg"
  port = "8000"
  protocol = "HTTP"
  vpc_id = aws_default_vpc.vpc_default.id
  count = var.is_production ? 1 : 0
}

resource "aws_lb_listener" "app_server_lb_listener" {
  load_balancer_arn = aws_lb.app_server_lb[0].arn
  port = "8000"
  protocol = "HTTP"
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.app_server_lb_target_group[0].arn
  }
  count = var.is_production ? 1 : 0
}

resource "aws_autoscaling_policy" "prod_autoscaling_policy" {
  name = "prod_autoscaling_policy"
  autoscaling_group_name = var.asg_name
  policy_type = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 50.0
  }
  count = var.is_production ? 1 : 0
}
