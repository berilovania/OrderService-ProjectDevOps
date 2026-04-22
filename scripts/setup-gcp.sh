#!/bin/bash
set -euo pipefail

# ============================================================
# setup-gcp.sh — Setup k3s + deploy order-service on GCP (e2-small)
# Usage: ssh into GCP VM as user 'gcp', then run: bash setup-gcp.sh <GITHUB_USER> [IMAGE_NAME] [DB_PASSWORD] [DOMAIN] [ACME_EMAIL]
# ============================================================

GITHUB_USER="${1:?Usage: bash setup-gcp.sh <GITHUB_USER> <DB_PASSWORD> <DOMAIN> <ACME_EMAIL> [IMAGE_NAME]}"
DB_PASSWORD="${2:?Error: DB_PASSWORD argument is required. Do not use weak defaults.}"
DOMAIN="${3:?Error: DOMAIN argument is required. Usage: bash setup-gcp.sh <GITHUB_USER> <DB_PASSWORD> <DOMAIN> <ACME_EMAIL> [IMAGE_NAME]}"
ACME_EMAIL="${4:?Error: ACME_EMAIL argument is required. Usage: bash setup-gcp.sh <GITHUB_USER> <DB_PASSWORD> <DOMAIN> <ACME_EMAIL> [IMAGE_NAME]}"
IMAGE_NAME="${5:-orderservice-projectdevops}"

if [ "${#DB_PASSWORD}" -lt 12 ]; then
  echo "ERROR: DB_PASSWORD must be at least 12 characters long." >&2
  exit 1
fi
IMAGE="ghcr.io/${GITHUB_USER}/${IMAGE_NAME}:latest"

echo "==> Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

if command -v k3s &>/dev/null; then
  echo "==> k3s already installed, skipping..."
else
  echo "==> Installing k3s (kubeconfig readable by current user, Traefik disabled)..."
  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644 --disable traefik
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

echo "==> Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml

echo "==> Waiting for NGINX Ingress Controller to be ready..."
kubectl rollout status deployment/ingress-nginx-controller -n ingress-nginx --timeout=120s

echo "==> Enabling NGINX snippet annotations..."
kubectl patch configmap ingress-nginx-controller \
  -n ingress-nginx \
  --type merge \
  -p '{"data":{"allow-snippet-annotations":"true"}}'
kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx
kubectl rollout status deployment/ingress-nginx-controller -n ingress-nginx --timeout=60s

echo "==> Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml

echo "==> Waiting for cert-manager to be ready..."
kubectl rollout status deployment/cert-manager -n cert-manager --timeout=120s
kubectl rollout status deployment/cert-manager-webhook -n cert-manager --timeout=120s
kubectl rollout status deployment/cert-manager-cainjector -n cert-manager --timeout=120s

echo "==> Waiting for cert-manager webhook to register..."
sleep 15

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
echo "  Login at https://${DOMAIN}/grafana with user: admin"

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

sed -i "s|__DOMAIN__|${DOMAIN}|g" k8s/ingress.yaml
sed -i "s|__ACME_EMAIL__|${ACME_EMAIL}|g" k8s/clusterissuer.yaml
sed -i "s|__DOMAIN__|${DOMAIN}|g" k8s/monitoring/grafana-deployment.yaml

echo "==> Pre-pulling images to avoid memory spike during pod startup..."
sudo k3s crictl pull postgres:16-alpine
echo "  postgres:16-alpine cached."

echo "==> Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/postgres-pvc.yaml
# Migrate from Deployment to StatefulSet (one-time, safe to repeat)
kubectl delete deployment postgres -n order-service --ignore-not-found
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/service.yaml

echo "==> Applying cert-manager ClusterIssuer..."
kubectl apply -f k8s/clusterissuer.yaml

echo "==> Applying Ingress..."
kubectl apply -f k8s/ingress.yaml

echo "==> Waiting for PostgreSQL pod to be Running..."
for i in $(seq 1 36); do
  STATUS=$(kubectl get pods -n order-service -l app=postgres --no-headers 2>/dev/null | awk '{print $3}' | head -1)
  echo "  postgres status: ${STATUS:-Pending} (${i}/36)"
  [ "$STATUS" = "Running" ] && break
  sleep 5
done

echo "==> Waiting for PostgreSQL to accept connections..."
for i in $(seq 1 30); do
  if kubectl exec -n order-service postgres-0 -- pg_isready -U orders -q 2>/dev/null; then
    echo "  PostgreSQL ready after ${i}x2s"
    break
  fi
  sleep 2
done

echo "==> Applying app deployment..."
kubectl apply -f k8s/deployment.yaml

echo "==> Waiting for order-service pod to be Running..."
for i in $(seq 1 60); do
  STATUS=$(kubectl get pods -n order-service -l app=order-service --no-headers 2>/dev/null | awk '{print $3}' | head -1)
  echo "  order-service status: ${STATUS:-Pending} (${i}/60)"
  [ "$STATUS" = "Running" ] && break
  sleep 5
done

echo "==> Deploying monitoring stack..."
kubectl apply -f k8s/monitoring/namespace.yaml
kubectl apply -f k8s/monitoring/network-policy.yaml
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-deployment.yaml
kubectl apply -f k8s/monitoring/prometheus-service.yaml
kubectl apply -f k8s/monitoring/grafana-datasource.yaml
kubectl apply -f k8s/monitoring/grafana-dashboard-provider.yaml
kubectl apply -f k8s/monitoring/grafana-dashboard.yaml
kubectl apply -f k8s/monitoring/grafana-deployment.yaml
kubectl apply -f k8s/monitoring/grafana-service.yaml
kubectl apply -f k8s/grafana-externalname-service.yaml
kubectl rollout status deployment/prometheus -n monitoring --timeout=120s
kubectl rollout status deployment/grafana -n monitoring --timeout=120s

echo ""
echo "==> Setup complete!"
echo "    Test (NodePort): curl http://localhost:30080/health"
echo "    Test (HTTPS):    curl https://${DOMAIN}/health"
echo "    Grafana:         https://${DOMAIN}/grafana (admin / ${GRAFANA_PASSWORD})"
echo ""
echo "    NOTE: TLS cert may take 1-2 minutes to issue after DNS propagates."
echo "    Check cert status: kubectl describe certificate order-service-tls -n order-service"
