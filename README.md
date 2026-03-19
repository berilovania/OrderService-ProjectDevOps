# Order Service — Projeto DevOps

Pipeline DevOps completo: FastAPI + Docker + Kubernetes (k3s) + GitHub Actions + AWS EC2.

## Stack

- **App**: Python/FastAPI — API REST de gerenciamento de pedidos
- **Container**: Docker multi-stage build
- **Orquestração**: Kubernetes (k3s) com 2 réplicas
- **CI/CD**: GitHub Actions → GHCR → Deploy via SSH
- **Cloud**: AWS EC2 (Ubuntu 22.04)
- **Observabilidade**: Prometheus metrics (`/metrics`)

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| GET | `/metrics` | Métricas Prometheus |
| GET | `/docs` | Swagger UI |
| POST | `/orders` | Criar pedido |
| GET | `/orders` | Listar pedidos |
| GET | `/orders/{id}` | Buscar pedido |
| PATCH | `/orders/{id}/status` | Atualizar status |
| DELETE | `/orders/{id}` | Cancelar pedido |

## Rodar localmente

```bash
# Instalar dependências
pip install -r app/requirements.txt

# Iniciar servidor
python -m uvicorn app.main:app --reload

# Acessar Swagger UI
# http://localhost:8000/docs
```

## Docker

```bash
docker build -t order-service .
docker run -p 8000:8000 order-service
```

## Deploy em produção

### 1. Criar EC2 na AWS

- Ubuntu 22.04 LTS, t3.small
- Security Group: portas 22, 30080, 6443
- Associar Elastic IP

### 2. Setup do servidor

```bash
scp -r k8s/ ubuntu@<EC2_IP>:~/k8s/
scp scripts/setup-ec2.sh ubuntu@<EC2_IP>:~/
ssh ubuntu@<EC2_IP> "bash setup-ec2.sh <GITHUB_USER>"
```

### 3. Configurar GitHub Secrets

- `EC2_HOST` — Elastic IP da EC2
- `EC2_SSH_KEY` — Chave privada SSH (conteúdo do `.pem`)

### 4. Deploy automático

Push na branch `main` → GitHub Actions builda a imagem, envia ao GHCR e atualiza o deployment na EC2.

## Gerar tráfego de teste

```bash
bash scripts/traffic.sh http://<EC2_IP>:30080
```

## Arquitetura

```
Developer → git push → GitHub Actions → GHCR (Docker image)
                                           ↓
                              EC2 (k3s) ← kubectl set image
                                ↓
                         order-service (2 pods)
                                ↓
                        NodePort :30080 → :8000
```
