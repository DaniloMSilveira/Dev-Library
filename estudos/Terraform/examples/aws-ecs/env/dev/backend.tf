terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "dev/terraform.tfstate"
    region = "us-west-2"
  }
}