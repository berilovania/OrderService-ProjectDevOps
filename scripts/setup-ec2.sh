#!/bin/bash
set -euo pipefail

# ============================================================
# setup-ec2.sh — Setup k3s + deploy order-service on Ubuntu EC2
# Usage: ssh into EC2, then run: bash setup-ec2.sh <GITHUB_USER> [IMAGE_NAME] [DB_PASSWORD]
# ============================================================

GITHUB_USER="${1:?Usage: bash setup-ec2.sh <GITHUB_USER> <DB_PASSWORD> [IMAGE_NAME]}"
DB_PASSWORD="${2:?Error: DB_PASSWORD argument is required. Do not use weak defaults.}"
IMAGE_NAME="${3:-orderservice-projectdevops}"

if [ "${#DB_PASSWORD}" -lt 12 ]; then
  echo "ERROR: DB_PASSWORD must be at least 12 characters long." >&2
  exit 1
fi
IMAGE="ghcr.io/${GITHUB_USER}/${IMAGE_NAME}:latest"

echo "==> Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

echo "==> Installing k3s (kubeconfig readable by ubuntu user)..."
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

echo "==> Configuring kubectl for current user..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown "$(id -u):$(id -g)" ~/.kube/config
export KUBECONFIG=~/.kube/config
echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc

echo "==> Waiting for k3s API to become available..."
until kubectl get nodes &>/dev/null; do
  echo "  k3s API not ready yet, retrying in 5s..."
  sleep 5
done

echo "==> Waiting for node to be Ready..."
kubectl wait --for=condition=Ready node --all --timeout=120s

echo "==> Creating GHCR pull secret..."
echo "Enter your GitHub Personal Access Token (with read:packages scope):"
read -r GHCR_TOKEN

kubectl create namespace order-service --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username="${GITHUB_USER}" \
  --docker-password="${GHCR_TOKEN}" \
  -n order-service \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Creating postgres secret..."
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD="${DB_PASSWORD}" \
  --from-literal=POSTGRES_USER="orders" \
  --from-literal=POSTGRES_DB="orders" \
  --namespace order-service \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Generating metrics token..."
METRICS_TOKEN=$(openssl rand -hex 32)
kubectl create secret generic metrics-token \
  --from-literal=metrics-token="${METRICS_TOKEN}" \
  --namespace order-service \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic metrics-token \
  --from-literal=metrics-token="${METRICS_TOKEN}" \
  --namespace monitoring \
  --dry-run=client -o yaml | kubectl apply -f -
echo "  Metrics token generated and stored. Save this for CI/CD METRICS_TOKEN secret: ${METRICS_TOKEN}"

echo "==> Generating Grafana admin password..."
GRAFANA_PASSWORD=$(openssl rand -base64 18)
kubectl create secret generic grafana-admin \
  --from-literal=admin-password="${GRAFANA_PASSWORD}" \
  --namespace monitoring \
  --dry-run=client -o yaml | kubectl apply -f -
echo "  Grafana admin password: ${GRAFANA_PASSWORD}"
echo "  Login with user: admin"

echo "==> Waiting for default service account to be created..."
until kubectl get serviceaccount default -n order-service &>/dev/null; do
  echo "  default SA not ready yet, retrying in 2s..."
  sleep 2
done

echo "==> Patching default service account..."
kubectl patch serviceaccount default \
  -n order-service \
  -p '{"imagePullSecrets": [{"name": "ghcr-secret"}]}'

echo "==> Replacing placeholders in deployment manifest..."
sed -i "s|__GITHUB_USER__|${GITHUB_USER}|g" k8s/deployment.yaml
sed -i "s|__IMAGE_NAME__|${IMAGE_NAME}|g" k8s/deployment.yaml

echo "==> Pre-pulling images to avoid memory spike during pod startup..."
sudo k3s crictl pull postgres:16-alpine
echo "  postgres:16-alpine cached."

echo "==> Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-pvc.yaml
# Migrate from Deployment to StatefulSet (one-time, safe to repeat)
kubectl delete deployment postgres -n order-service --ignore-not-found
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/service.yaml

echo "==> Waiting for PostgreSQL pod to be Running..."
for i in $(seq 1 36); do
  STATUS=$(kubectl get pods -n order-service -l app=postgres --no-headers 2>/dev/null | awk '{print $3}' | head -1)
  echo "  postgres status: ${STATUS:-Pending} (${i}/36)"
  [ "$STATUS" = "Running" ] && break
  sleep 5
done

sleep 10

echo "==> Applying app deployment..."
kubectl apply -f k8s/deployment.yaml

echo "==> Waiting for order-service pod to be Running..."
for i in $(seq 1 60); do
  STATUS=$(kubectl get pods -n order-service -l app=order-service --no-headers 2>/dev/null | awk '{print $3}' | head -1)
  echo "  order-service status: ${STATUS:-Pending} (${i}/60)"
  [ "$STATUS" = "Running" ] && break
  sleep 5
done

echo ""
echo "==> Setup complete!"
echo "    Test: curl http://localhost:30080/health"
echo "    Swagger: http://<EC2_PUBLIC_IP>:30080/docs"
