resource "aws_security_group" "alb_security_group" {
  name        = "ecs_alb"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_security_group_rule" "ingress_tcp_alb" {
  type              = "ingress"
  from_port         = 8000
  to_port           = 8000
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"] #0.0.0.0 - 255.255.255.255
  security_group_id = aws_security_group.alb_security_group.id
}

resource "aws_security_group_rule" "egress_alb" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"] #0.0.0.0 - 255.255.255.255
  security_group_id = aws_security_group.alb_security_group.id
}

resource "aws_security_group" "private_security_group" {
  name        = "ecs_private"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_security_group_rule" "ingress_ecs" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  source_security_group_id = aws_security_group.alb_security_group.id
  security_group_id = aws_security_group.private_security_group.id
}

resource "aws_security_group_rule" "egress_ecs" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"] #0.0.0.0 - 255.255.255.255
  security_group_id = aws_security_group.private_security_group.id
}