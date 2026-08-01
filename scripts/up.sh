#!/bin/bash
set -e

echo "==> Provisioning infrastructure with Terraform..."
cd terraform
terraform init -upgrade -backend-config=backend.hcl
terraform apply
cd ..

echo "==> Updating kubeconfig..."
aws eks update-kubeconfig --region ap-south-1 --name url-shortener

echo "==> Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml
echo "Waiting for cert-manager to be ready..."
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=180s

echo "==> Installing ingress-nginx controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/aws/deploy.yaml
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s

echo "==> Creating secrets (redis, grafana)..."
./scripts/create-secrets.sh

echo "==> Applying Kubernetes manifests..."
kubectl apply -f k8s/redis/
kubectl apply -f k8s/tls/
kubectl apply -f k8s/app/
kubectl apply -f k8s/observability/

echo "==> Certificate status:"
kubectl get certificate

echo "==> Waiting for rollouts..."
kubectl rollout status deployment/redis --timeout=180s
kubectl rollout status deployment/url-shortener --timeout=180s
kubectl rollout status deployment/url-shortener-frontend --timeout=180s
kubectl rollout status deployment/prometheus --timeout=180s
kubectl rollout status deployment/grafana --timeout=180s

echo "==> Done. Ingress address:"
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
echo
echo "Test with: curl -k -H \"Host: url-shortener.local\" https://<address-above>/health"
