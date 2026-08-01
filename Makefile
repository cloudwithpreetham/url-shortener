.PHONY: up down status

up:
	@./scripts/up.sh

down:
	@./scripts/down.sh

status:
	@kubectl get pods
	@kubectl get svc -n ingress-nginx
