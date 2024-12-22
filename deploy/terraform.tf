terraform {
  backend "s3" {
    bucket = "tna-update-tf-backend-781234"
    key    = "terraformstate"
    region = "eu-west-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
