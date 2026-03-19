# Order Service — Projeto DevOps

Pipeline DevOps completo demonstrando containerização, orquestração e entrega contínua em nuvem.

## O que é este projeto?

Uma API REST de gerenciamento de pedidos construída com **FastAPI/Python**, usada como base para demonstrar um pipeline DevOps de ponta a ponta:

- **Aplicação**: API REST com CRUD de pedidos, métricas Prometheus e interface web customizada
- **Containerização**: Docker com multi-stage build para imagem enxuta
- **Orquestração**: Kubernetes (k3s) com 2 réplicas, health checks e resource limits
- **CI/CD**: GitHub Actions que builda, publica no GHCR e deploya automaticamente via SSH
- **Cloud**: AWS EC2 (Ubuntu 22.04) com Elastic IP

```
Developer → git push → GitHub Actions → GHCR (Docker image)
                                           ↓
                              EC2 (k3s) ← kubectl set image
                                ↓
                         order-service (2 réplicas)
                                ↓
                        NodePort :30080 → :8000
```

### Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Dashboard web |
| GET | `/health` | Health check |
| GET | `/metrics` | Métricas Prometheus |
| GET | `/docs` | Documentação da API |
| POST | `/orders` | Criar pedido |
| GET | `/orders` | Listar pedidos |
| GET | `/orders/{id}` | Buscar pedido |
| PATCH | `/orders/{id}/status` | Atualizar status |
| DELETE | `/orders/{id}` | Cancelar pedido |

---

## Como rodar

### Localmente (desenvolvimento)

**Pré-requisitos:** Python 3.12+

```bash
# 1. Instalar dependências
pip install -r app/requirements.txt

# 2. Iniciar o servidor com hot reload
python -m uvicorn app.main:app --reload

# 3. Acessar
# Dashboard:  http://localhost:8000/
# Docs:       http://localhost:8000/docs
# Métricas:   http://localhost:8000/metrics
```

### Com Docker

**Pré-requisitos:** Docker instalado

```bash
# 1. Buildar a imagem
docker build -t order-service .

# 2. Rodar o container
docker run -p 8000:8000 order-service

# 3. Acessar em http://localhost:8000
```

### Em produção (AWS EC2 + Kubernetes)

#### Passo 1 — Criar EC2 na AWS

- AMI: Ubuntu 22.04 LTS
- Tipo: t3.small (mínimo)
- Security Group: liberar portas `22` (SSH), `30080` (app), `6443` (k8s API)
- Associar um Elastic IP à instância

#### Passo 2 — Provisionar o servidor

```bash
# Copiar manifests e script para a EC2
scp -r k8s/ ubuntu@<EC2_IP>:~/k8s/
scp scripts/setup-ec2.sh ubuntu@<EC2_IP>:~/

# Executar o setup (instala k3s, cria secrets, aplica manifests)
ssh ubuntu@<EC2_IP> "bash setup-ec2.sh <SEU_USUARIO_GITHUB>"
```

O script irá pedir um **Personal Access Token** do GitHub com escopo `read:packages` para autenticar no GHCR.

#### Passo 3 — Configurar GitHub Secrets

No repositório, vá em **Settings → Secrets and variables → Actions** e adicione:

| Secret | Valor |
|--------|-------|
| `EC2_HOST` | Elastic IP da EC2 |
| `EC2_SSH_KEY` | Conteúdo do arquivo `.pem` da EC2 |

#### Passo 4 — Atualizar o manifesto Kubernetes

Em [k8s/deployment.yaml](k8s/deployment.yaml), substitua `OWNER` pelo seu usuário GitHub:

```yaml
image: ghcr.io/<SEU_USUARIO_GITHUB>/projeto-devops:latest
```

#### Passo 5 — Deploy automático

A partir daqui, qualquer push na branch `main` dispara o pipeline automaticamente:

1. GitHub Actions builda a imagem Docker
2. Publica no GHCR com a tag do commit SHA
3. Conecta via SSH na EC2 e executa `kubectl set image`
4. Aguarda o rollout completar (timeout: 120s)

```bash
git push origin main  # deploy automático acionado
```

#### Verificar o deploy

```bash
# Na EC2
kubectl get pods -n order-service
kubectl rollout status deployment/order-service -n order-service

# Testar a API
curl http://<EC2_IP>:30080/health
```

#### Gerar tráfego de teste

```bash
bash scripts/traffic.sh http://<EC2_IP>:30080
```
