terraform {
  backend "s3" {
    bucket = "terraform-state-eks"
    key    = "prod/terraform.tfstate"
    region = "us-west-2"
  }
}