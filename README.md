# Order Service

API REST de gerenciamento de pedidos com pipeline DevOps completo — do código ao deploy automatizado em nuvem.

## Sobre o Projeto

O **Order Service** é uma aplicação de gerenciamento de pedidos que cobre todo o ciclo DevOps: desenvolvimento, containerização, orquestração e entrega contínua. A API permite criar, listar, atualizar e cancelar pedidos, com persistência em PostgreSQL, métricas Prometheus, dashboard interativo e deploy automatizado em Kubernetes via GitHub Actions.

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| **Linguagem** | Python 3.12 |
| **Framework** | FastAPI (async) |
| **Banco de dados** | PostgreSQL 16 + SQLAlchemy (async) + asyncpg |
| **Containerização** | Docker (multi-stage build) |
| **Orquestração** | Kubernetes (k3s) |
| **CI/CD** | GitHub Actions |
| **Registry** | GitHub Container Registry (GHCR) |
| **Monitoramento** | Prometheus (via prometheus-fastapi-instrumentator) |
| **Cloud** | AWS EC2 (Ubuntu 22.04) |

## Arquitetura

```
                         ┌──────────────┐
                         │  git push    │
                         │  (main)      │
                         └──────┬───────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   GitHub Actions    │
                     │                     │
                     │  1. Build imagem    │
                     │  2. Push → GHCR    │
                     │  3. SSH na EC2     │
                     │  4. kubectl apply  │
                     └─────────┬───────────┘
                               │
                               ▼
                  ┌───────────────────────────┐
                  │      EC2 (k3s)            │
                  │                           │
                  │  ┌─────────────────────┐  │
                  │  │  order-service      │  │
                  │  │  (2 réplicas)       │  │
                  │  │  porta 8000         │  │
                  │  └────────┬────────────┘  │
                  │           │               │
                  │           ▼               │
                  │  ┌─────────────────────┐  │
                  │  │  PostgreSQL 16      │  │
                  │  │  (1 réplica + PVC)  │  │
                  │  │  porta 5432         │  │
                  │  └─────────────────────┘  │
                  │                           │
                  │  NodePort :30080 → :8000  │
                  └───────────────────────────┘
```

## Funcionalidades

### API REST completa
- **Criar pedido** — recebe cliente, itens e valor total, gera UUID e timestamp automaticamente
- **Listar pedidos** — paginação com `skip` e `limit`, ordenado por data (mais recente primeiro)
- **Buscar por ID** — retorna um pedido específico pelo UUID
- **Atualizar status** — transição de status: `created → processing → completed`
- **Cancelar pedido** — marca o pedido como `cancelled` (pedidos cancelados não aceitam mais atualizações)

### Dashboard web interativo
- Interface customizada em `/` com listagem de pedidos em tempo real (polling a cada 8s)
- Cards de estatísticas: total, criados, processando, concluídos
- Criação de pedidos de teste direto pelo dashboard
- Paginação client-side (10 pedidos por página)
- Tema claro/escuro com persistência no `localStorage`
- Internacionalização PT-BR / EN

### Documentação interativa
- Swagger UI customizado em `/docs` com tema integrado (claro/escuro)
- Permite testar todos os endpoints diretamente pelo navegador

### Monitoramento
- Métricas Prometheus em `/metrics` (latência, contagem de requests, status codes)
- Health check em `/health` com verificação de conectividade ao banco

### Limpeza automática
- Task em background que roda a cada hora e remove pedidos com mais de 24h (configurável via `DATA_RETENTION_HOURS`)

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Dashboard web |
| `GET` | `/health` | Health check (verifica conexão com o banco) |
| `GET` | `/metrics` | Métricas Prometheus |
| `GET` | `/docs` | Swagger UI customizado |
| `POST` | `/orders` | Criar pedido |
| `GET` | `/orders` | Listar pedidos (`?skip=0&limit=50`) |
| `GET` | `/orders/{id}` | Buscar pedido por ID |
| `PATCH` | `/orders/{id}/status` | Atualizar status |
| `DELETE` | `/orders/{id}` | Cancelar pedido |

### Exemplo de uso

**Criar um pedido:**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "João Silva",
    "items": ["Notebook Pro", "Mouse Gamer"],
    "total": 4599.90
  }'
```

**Resposta:**
```json
{
  "id": "a1b2c3d4-...",
  "customer": "João Silva",
  "items": ["Notebook Pro", "Mouse Gamer"],
  "total": 4599.90,
  "status": "created",
  "created_at": "2026-03-19T12:00:00Z"
}
```

**Atualizar status:**
```bash
curl -X PATCH http://localhost:8000/orders/{id}/status \
  -H "Content-Type: application/json" \
  -d '{"status": "processing"}'
```

**Cancelar pedido:**
```bash
curl -X DELETE http://localhost:8000/orders/{id}
```

## Estrutura do Projeto

```
.
├── app/
│   ├── main.py            # Entrypoint FastAPI (lifespan, rotas, cleanup)
│   ├── routes.py          # Endpoints CRUD /orders
│   ├── models.py          # Schemas Pydantic (OrderCreate, Order, StatusUpdate)
│   ├── database.py        # Engine async SQLAlchemy + sessão
│   ├── db_models.py       # Modelo ORM (tabela orders)
│   ├── metrics.py         # Configuração Prometheus
│   ├── dashboard.py       # HTML do dashboard (/)
│   ├── docs_page.py       # HTML do Swagger customizado (/docs)
│   └── requirements.txt   # Dependências Python
├── k8s/
│   ├── namespace.yaml
│   ├── postgres-secret.yaml
│   ├── postgres-pvc.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── scripts/
│   ├── setup-ec2.sh       # Provisionamento da EC2 (k3s + manifests)
│   └── traffic.sh         # Gerador de tráfego para testes
├── .github/workflows/
│   └── deploy.yml         # Pipeline CI/CD
├── Dockerfile             # Multi-stage build
├── docker-compose.yml     # Stack local (app + PostgreSQL)
└── .env.example           # Variáveis de ambiente
```

## Como Executar

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- (Opcional) **Python 3.12+** para rodar sem Docker

---

### Opção 1 — Docker Compose (recomendado)

A forma mais simples. Sobe a aplicação e o PostgreSQL com um único comando.

```bash
# 1. Clonar o repositório
git clone https://github.com/<seu-usuario>/Projeto-devops.git
cd Projeto-devops

# 2. (Opcional) Ajustar variáveis de ambiente
cp .env.example .env

# 3. Subir os serviços
docker compose up
```

Acesse:
- **Dashboard:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Métricas:** http://localhost:8000/metrics
- **Health:** http://localhost:8000/health

Para parar: `Ctrl+C` ou `docker compose down`

---

### Opção 2 — Docker (sem Compose)

Útil quando você já tem um PostgreSQL rodando.

```bash
# 1. Build da imagem
docker build -t order-service .

# 2. Rodar o container
docker run -p 8000:8000 \
  -e DATABASE_HOST=host.docker.internal \
  -e DATABASE_USER=orders \
  -e DATABASE_PASSWORD=orders \
  -e DATABASE_NAME=orders \
  order-service
```

> `host.docker.internal` permite o container acessar um PostgreSQL rodando na máquina host.

---

### Opção 3 — Localmente (desenvolvimento)

```bash
# 1. Instalar dependências
pip install -r app/requirements.txt

# 2. Subir um PostgreSQL (via Docker, por exemplo)
docker run -d --name postgres \
  -e POSTGRES_USER=orders \
  -e POSTGRES_PASSWORD=orders \
  -e POSTGRES_DB=orders \
  -p 5432:5432 \
  postgres:16-alpine

# 3. Iniciar a aplicação com hot reload
python -m uvicorn app.main:app --reload
```

---

### Gerar tráfego de teste

O script `traffic.sh` cria pedidos automaticamente e percorre o ciclo de vida completo (`created → processing → completed`).

```bash
# Ciclo único (3 pedidos)
bash scripts/traffic.sh http://localhost:8000

# Loop contínuo (Ctrl+C para parar)
bash scripts/traffic.sh --loop http://localhost:8000

# Personalizado: 5 pedidos por ciclo, intervalo de 15s, 10 ciclos
bash scripts/traffic.sh --loop --orders 5 --interval 15 --count 10 http://localhost:8000
```

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_HOST` | `localhost` | Host do PostgreSQL |
| `DATABASE_PORT` | `5432` | Porta do PostgreSQL |
| `DATABASE_USER` | `orders` | Usuário do banco |
| `DATABASE_PASSWORD` | `orders` | Senha do banco |
| `DATABASE_NAME` | `orders` | Nome do banco |
| `DATA_RETENTION_HOURS` | `24` | Horas para manter pedidos antes da limpeza automática |

## Deploy em Produção (AWS EC2 + Kubernetes)

### 1. Criar a instância EC2

- **AMI:** Ubuntu 22.04 LTS
- **Tipo:** t3.small (mínimo)
- **Security Group:** liberar portas `22` (SSH), `30080` (aplicação), `6443` (API do Kubernetes)
- Associar um **Elastic IP** à instância

### 2. Provisionar o servidor

```bash
# Copiar arquivos para a EC2
scp -r k8s/ scripts/setup-ec2.sh ubuntu@<EC2_IP>:~/

# Executar o setup (instala k3s, cria secrets, aplica manifests)
ssh ubuntu@<EC2_IP> "bash setup-ec2.sh <SEU_USUARIO_GITHUB>"
```

O script pedirá um **Personal Access Token** do GitHub com escopo `read:packages` para autenticar no GHCR.

### 3. Configurar GitHub Secrets

No repositório, vá em **Settings → Secrets and variables → Actions** e adicione:

| Secret | Valor |
|--------|-------|
| `EC2_HOST` | Elastic IP da instância |
| `EC2_SSH_KEY` | Conteúdo do arquivo `.pem` |
| `DB_PASSWORD` | Senha do PostgreSQL |

### 4. Deploy automático

A partir daqui, qualquer push na branch `main` aciona o pipeline:

1. **Build** — GitHub Actions compila a imagem Docker
2. **Push** — Publica no GHCR com tag do commit SHA + `latest`
3. **Deploy** — Conecta via SSH na EC2, aplica os manifests e atualiza a imagem com `kubectl set image`
4. **Rollout** — Aguarda a atualização completar (timeout: 120s)

```bash
git push origin main  # deploy automático
```

### Verificar o deploy

```bash
# Na EC2
kubectl get pods -n order-service
kubectl rollout status deployment/order-service -n order-service

# Testar externamente
curl http://<EC2_IP>:30080/health
```

## Recursos do Kubernetes

| Recurso | Nome | Detalhes |
|---------|------|----------|
| Namespace | `order-service` | Isola todos os recursos |
| Deployment | `order-service` | 2 réplicas, liveness/readiness probes, resource limits |
| Deployment | `postgres` | 1 réplica, volume persistente |
| Service | `order-service` | NodePort 30080 → 8000 |
| Service | `postgres` | ClusterIP 5432 (acesso interno) |
| PVC | `postgres-pvc` | 1Gi para dados do PostgreSQL |
| Secret | `postgres-secret` | Credenciais do banco |

---

Desenvolvido por **Matheus Santos Caldas**
