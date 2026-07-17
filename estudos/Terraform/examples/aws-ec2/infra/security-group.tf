resource "aws_security_group" "full-access" {
  name        = var.security_group
  description = "Security group for ${var.environment}"

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
  }

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
  }

  tags = {
    Name = "full-access-${var.environment}"
  }
}