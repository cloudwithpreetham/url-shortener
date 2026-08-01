#!/bin/bash
set -e

BUCKET="url-shortener-tfstate-$(aws sts get-caller-identity --query Account --output text)"
REGION="ap-south-1"

echo "Creating bucket: $BUCKET"
aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --create-bucket-configuration LocationConstraint="$REGION"

aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "bucket = \"$BUCKET\"" > terraform/backend.hcl

echo "Done. Bucket name: $BUCKET"
echo "Wrote terraform/backend.hcl (gitignored) for use with: terraform init -backend-config=backend.hcl"
