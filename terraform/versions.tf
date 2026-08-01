terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: move state to an S3 backend once you have a bucket for it.
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "url-shortener/terraform.tfstate"
  #   region = "us-west-2"
  # }
}

provider "aws" {
  region = var.aws_region
}
