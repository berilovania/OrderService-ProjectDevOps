# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r app/requirements.txt

# Run locally (hot reload)
python -m uvicorn app.main:app --reload

# Build Docker image
docker build -t order-service .

# Run container
docker run -p 8000:8000 order-service

# Generate test traffic
bash scripts/traffic.sh http://localhost:8000
```

## Architecture

This is a **FastAPI order management service** built as a full DevOps showcase:

```
Developer → git push → GitHub Actions → GHCR (Docker image)
                                           ↓
                              EC2 (k3s) ← kubectl set image
                                ↓
                         order-service (2 pods)
                                ↓
                        NodePort :30080 → :8000
```

### App layer (`app/`)

- **`main.py`** — FastAPI app entrypoint. Disables default `/docs` and `/redoc` to serve custom HTML pages instead. Mounts `router` and exposes Prometheus metrics.
- **`routes.py`** — All CRUD endpoints for `/orders`. Uses an in-memory `dict` as storage (no database — data is lost on restart).
- **`models.py`** — Pydantic models: `OrderCreate` (input), `Order` (full entity with UUID + timestamp), `StatusUpdate`. Status is an enum: `created → processing → completed / cancelled`.
- **`metrics.py`** — Configures `prometheus-fastapi-instrumentator`, excluded from `/metrics` handler itself.
- **`dashboard.py`** — Returns custom HTML for the `GET /` root route.
- **`docs_page.py`** — Returns custom HTML for `GET /docs` (replaces Swagger UI default).

### Infrastructure

- **`Dockerfile`** — Multi-stage build: installs deps in `builder`, copies only runtime artifacts to final `python:3.12-slim` image.
- **`k8s/`** — Kubernetes manifests: namespace, deployment (2 replicas, liveness/readiness on `/health`), NodePort service on port 30080.
- **`scripts/setup-ec2.sh`** — One-shot provisioning script: installs k3s, creates GHCR pull secret, applies k8s manifests.
- **`.github/workflows/deploy.yml`** — CI/CD: on push to `main`, builds+pushes image to GHCR tagged with commit SHA, then SSHes into EC2 and runs `kubectl set image`.

### Key design notes

- **No database**: orders live in memory in `routes.py`. Restarting the pod or deploying a new version clears all orders.
- **Custom UI**: Swagger UI is disabled (`docs_url=None`); both `/` and `/docs` serve hand-crafted HTML from `dashboard.py` and `docs_page.py`.
- **Prometheus**: metrics exposed at `/metrics` via `instrumentator.expose(app)`.
- **GitHub Secrets required for CI/CD**: `EC2_HOST` (Elastic IP) and `EC2_SSH_KEY` (private key content). The `GITHUB_TOKEN` is used automatically for GHCR auth.
- **k8s deployment update**: `k8s/deployment.yaml` has a placeholder `OWNER` in the image name — replace with your actual GitHub username before first deploy.
