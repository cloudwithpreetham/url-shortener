# URL Shortener — STAR Method Summary

## Situation

I wanted to build a project that went beyond just writing an application — something that demonstrated the full lifecycle of shipping and operating software the way a real engineering team would, from infrastructure provisioning through deployment, security, and monitoring.

## Task

I set out to build and deploy a full-stack URL shortener — Flask backend, Redis for storage, Nginx-served frontend — but the actual goal wasn't the app itself. It was standing up a complete, production-style DevOps pipeline around it: infrastructure as code, automated CI/CD, container orchestration on Kubernetes, secured secrets, TLS, and observability, all while being deliberate about cloud cost.

## Action

- **Provisioned AWS infrastructure with Terraform** — a VPC across two availability zones, an EKS cluster, and a managed node group, with remote state stored in S3 using native locking so the state file isn't a single point of failure.

- **Built a CI/CD pipeline in GitHub Actions** — every push runs lint and test stages, then builds and pushes separate backend and frontend Docker images, then rolls them out to the cluster automatically. Debugged real pipeline failures along the way — wrong build contexts, missing dependencies, a GitHub account-level Actions restriction — which built real operational experience with CI/CD, not just writing YAML that looks right.

- **Designed the Kubernetes routing** — the tricky part was that one backend route was a wildcard at the root path (`/<code>` for redirects), which could collide with the frontend also serving at root. Solved with Ingress path priority: exact match for `/` routes to the frontend, prefix match falls through to the backend.

- **Secured the deployment** — added Redis authentication via Kubernetes Secrets, and TLS termination at the ingress using cert-manager, verified working correctly at the TLS handshake level (SNI/SAN inspection), not just that HTTPS responded.

- **Added real observability** — instrumented the Flask app with Prometheus metrics, confirmed Prometheus was actively scraping live data, and wired up Grafana as the visualization layer.

- **Wrote automated tests and cost-conscious automation** — a pytest suite with mocked dependencies gated into the CI pipeline, and a `make up` / `make down` workflow so the whole stack — VPC, EKS, ingress, TLS, app, monitoring — can be reproducibly stood up or torn down in one command, since none of this is free-tier eligible.

## Result

The result is a fully working, reproducible deployment — the entire stack can be spun up from scratch with one command, producing a live, TLS-secured, monitored application running on EKS within minutes, and torn down just as cleanly to control cost. Along the way, several real-world issues were hit and resolved — Docker build context mismatches, Kubernetes pod scheduling limits tied to instance networking capacity, DNS propagation delays on newly provisioned load balancers — providing hands-on debugging experience with problems that don't surface until something is actually deployed for real.

<!-- ---

## Delivery Notes

- Keep the **Result** short and punchy in a first pass, then let the interviewer pull threads — "tell me about a challenge" is a natural cue to go deeper into one of the debugging stories (pod scheduling limit or Ingress routing design are the most technically interesting).
- For technical interviewers, the wildcard-route-vs-static-frontend Ingress problem is a strong one to lead with — it's a genuine design decision, not boilerplate.
- Avoid over-claiming "production-grade." Known, honest gaps: self-signed TLS (no real domain), ephemeral Redis storage (data lost on pod restart), single-node cluster (no autoscaling). Having a ready answer for "what would you do differently for production" reads as more senior than pretending the project is flawless. -->
