#!/bin/bash
set -e

read -sp "Enter Redis password: " REDIS_PASSWORD
echo
read -sp "Enter Grafana admin password: " GRAFANA_PASSWORD
echo

kubectl create secret generic redis-secret \
  --from-literal=password="$REDIS_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic grafana-admin \
  --from-literal=password="$GRAFANA_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets created/updated."
