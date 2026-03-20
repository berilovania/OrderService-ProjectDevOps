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

check_step() {
  echo ""
  echo ">>> ETAPA: $1"
  echo "    Pressione ENTER para continuar ou Ctrl+C para abortar."
  read -r
}

echo "==> Atualizando sistema..."
sudo apt-get update && sudo apt-get upgrade -y

check_step "Instalação do k3s"

if command -v k3s &>/dev/null; then
  echo "==> k3s já instalado, pulando instalação..."
else
  echo "==> Instalando k3s (kubeconfig legível pelo usuário gcp)..."
  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
fi

echo "==> Configurando kubectl para o usuário atual..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown "$(id -u):$(id -g)" ~/.kube/config
export KUBECONFIG=~/.kube/config
echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc

echo "==> Aguardando a API do k3s ficar disponível..."
until kubectl get nodes &>/dev/null; do
  echo "  API do k3s ainda não pronta, tentando em 5s..."
  sleep 5
done

echo "==> Aguardando o node ficar Ready..."
kubectl wait --for=condition=Ready node --all --timeout=120s

check_step "Criação de secrets (GHCR + postgres)"

echo "==> Criando secret de pull do GHCR..."
echo "Digite seu GitHub Personal Access Token (com escopo read:packages):"
read -r GHCR_TOKEN

kubectl create namespace order-service --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username="${GITHUB_USER}" \
  --docker-password="${GHCR_TOKEN}" \
  -n order-service \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Criando secret do postgres..."
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD="${DB_PASSWORD}" \
  --from-literal=POSTGRES_USER="orders" \
  --from-literal=POSTGRES_DB="orders" \
  --namespace order-service \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Aguardando service account default ser criado..."
until kubectl get serviceaccount default -n order-service &>/dev/null; do
  echo "  default SA ainda não pronto, tentando em 2s..."
  sleep 2
done

echo "==> Configurando imagePullSecrets no service account default..."
kubectl patch serviceaccount default \
  -n order-service \
  -p '{"imagePullSecrets": [{"name": "ghcr-secret"}]}'

echo "==> Substituindo placeholders no manifesto de deployment..."
sed -i "s|__GITHUB_USER__|${GITHUB_USER}|g" k8s/deployment.yaml
sed -i "s|__IMAGE_NAME__|${IMAGE_NAME}|g" k8s/deployment.yaml

check_step "Apply dos manifests de infraestrutura (namespace, PVC, postgres)"

echo "==> Fazendo pre-pull da imagem postgres para evitar spike de memória..."
sudo k3s crictl pull postgres:16-alpine
echo "  postgres:16-alpine em cache."

echo "==> Aplicando manifests Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/service.yaml

echo "==> Aguardando pod do PostgreSQL ficar Running..."
for i in $(seq 1 36); do
  STATUS=$(kubectl get pods -n order-service -l app=postgres --no-headers 2>/dev/null | awk '{print $3}' | head -1)
  echo "  status postgres: ${STATUS:-Pending} (${i}/36)"
  [ "$STATUS" = "Running" ] && break
  sleep 5
done

sleep 10

check_step "Apply do deployment da aplicação (order-service)"

echo "==> Aplicando deployment da aplicação..."
kubectl apply -f k8s/deployment.yaml

echo "==> Aguardando pod do order-service ficar Running..."
for i in $(seq 1 60); do
  STATUS=$(kubectl get pods -n order-service -l app=order-service --no-headers 2>/dev/null | awk '{print $3}' | head -1)
  echo "  status order-service: ${STATUS:-Pending} (${i}/60)"
  [ "$STATUS" = "Running" ] && break
  sleep 5
done

echo ""
echo "==> Setup completo!"
echo "    Teste: curl http://localhost:30080/health"
echo "    Swagger: http://<GCP_EXTERNAL_IP>:30080/docs"
