#!/bin/bash
set -e

echo "==> Removing ingress-nginx controller (releases the NLB)..."
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/aws/deploy.yaml --ignore-not-found

echo "==> Waiting for NLB to fully deprovision..."
sleep 30

echo "==> Destroying Terraform-managed infrastructure..."
cd terraform
terraform destroy
cd ..

echo "==> Done. Verifying cleanup..."
aws eks list-clusters --region ap-south-1
aws elbv2 describe-load-balancers --region ap-south-1 --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-ingressn')]"
