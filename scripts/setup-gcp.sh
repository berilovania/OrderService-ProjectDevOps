#!/bin/bash
set -euo pipefail

# ============================================================
# setup-gcp.sh — Setup k3s + deploy order-service on GCP (e2-small)
# Usage: ssh into GCP VM as user 'gcp', then run: bash setup-gcp.sh <GITHUB_USER> [IMAGE_NAME] [DB_PASSWORD]
# ============================================================

GITHUB_USER="${1:?Usage: bash setup-gcp.sh <GITHUB_USER>}"
IMAGE_NAME="${2:-orderservice-projectdevops}"
DB_PASSWORD="${3:-orderpass}"
IMAGE="ghcr.io/${GITHUB_USER}/${IMAGE_NAME}:latest"

echo "==> Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

if command -v k3s &>/dev/null; then
  echo "==> k3s already installed, skipping..."
else
  echo "==> Installing k3s (kubeconfig readable by current user)..."
  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
fi

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

echo "==> Waiting for default service account..."
until kubectl get serviceaccount default -n order-service &>/dev/null; do
  echo "  default SA not ready yet, retrying in 2s..."
  sleep 2
done

echo "==> Patching default service account with imagePullSecrets..."
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
echo "    Swagger: http://<GCP_EXTERNAL_IP>:30080/docs"
