terraform {
  backend "s3" {
    bucket = "terraform-state-eks"
    key    = "dev/terraform.tfstate"
    region = "us-west-2"
  }
}