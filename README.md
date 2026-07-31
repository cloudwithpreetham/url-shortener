# URL Shortener

A simple full-stack URL shortener built to demonstrate a complete DevOps workflow:
containerization → CI/CD → Kubernetes deployment → monitoring.

## Architecture

- **Frontend:** Static HTML/JS served via Nginx
- **Backend:** Python Flask REST API (Gunicorn in production)
- **Database:** Redis (key-value store for short code → URL mapping)

## API Endpoints

| Method | Endpoint         | Description                          |
|--------|------------------|---------------------------------------|
| POST   | `/shorten`       | Body: `{"url": "..."}` → returns short code |
| GET    | `/<code>`        | Redirects to the original long URL   |
| GET    | `/stats/<code>`  | Returns metadata for a short code    |
| GET    | `/health`        | Health check (used by K8s probes)    |

## Running Locally

Requires Docker and Docker Compose.

```bash
docker-compose up --build
```

- Frontend: http://localhost:8080
- Backend API: http://localhost:5000
- Redis: localhost:6379

## Running Without Docker (backend only)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run Redis separately, e.g.:
# docker run -p 6379:6379 redis:7-alpine

python app.py
```

## Project Roadmap

- [x] Containerized frontend, backend, and Redis
- [ ] CI/CD pipeline (GitHub Actions) building and pushing images
- [ ] Kubernetes manifests / Helm chart for deployment
- [ ] Terraform for provisioning the cluster infrastructure
- [ ] Prometheus + Grafana monitoring stack
# trigger
