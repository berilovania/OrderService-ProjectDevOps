# Order Service — Pipeline DevOps Completo

Pipeline CI/CD de ponta a ponta com containerização Docker, orquestração Kubernetes e deploy automatizado em nuvem AWS. Do `git push` à produção em minutos, sem intervenção manual.

---

## 1. Visão Geral do Projeto

Este projeto implementa um **pipeline DevOps completo e funcional**, cobrindo todas as etapas do ciclo de vida de entrega de software: versionamento, integração contínua, containerização, registro de imagens, orquestração e deploy automatizado em ambiente cloud real.

A aplicação — uma API REST de gerenciamento de pedidos construída com FastAPI — serve como **carga de trabalho para validar a infraestrutura**. O foco do projeto não está na lógica de negócio, mas sim na demonstração prática de:

- **Automação completa** — zero intervenção manual entre o commit e a produção
- **Infraestrutura como código** — manifests Kubernetes versionados no repositório
- **Deploy real em nuvem** — cluster Kubernetes rodando em instância AWS EC2
- **Boas práticas de containerização** — imagem Docker otimizada com multi-stage build
- **Observabilidade** — métricas Prometheus, health checks e probes de liveness/readiness

---

## 2. Arquitetura

O fluxo de entrega segue o modelo GitOps simplificado: o repositório é a fonte da verdade, e qualquer alteração na branch `main` dispara automaticamente o pipeline completo.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FLUXO DE ENTREGA                              │
│                                                                      │
│   Developer                                                          │
│      │                                                               │
│      ▼                                                               │
│   git push (main)                                                    │
│      │                                                               │
│      ▼                                                               │
│   ┌─────────────────────────────────────┐                            │
│   │        GitHub Actions (CI/CD)       │                            │
│   │                                     │                            │
│   │  1. Checkout do código              │                            │
│   │  2. Build da imagem Docker          │                            │
│   │  3. Push para GHCR (tag: SHA)       │                            │
│   │  4. Copia manifests para EC2 (SCP)  │                            │
│   │  5. Deploy via SSH + kubectl        │                            │
│   └──────────────────┬──────────────────┘                            │
│                      │                                               │
│                      ▼                                               │
│   ┌──────────────────────────────────────────────┐                   │
│   │            AWS EC2 (Ubuntu 22.04)            │                   │
│   │                                              │                   │
│   │   ┌──────────────────────────────────────┐   │                   │
│   │   │          Cluster k3s                 │   │                   │
│   │   │                                      │   │                   │
│   │   │   ┌────────────────────────────┐     │   │                   │
│   │   │   │   order-service (2 pods)   │     │   │                   │
│   │   │   │   porta 8000               │     │   │                   │
│   │   │   │   liveness + readiness     │     │   │                   │
│   │   │   └────────────┬───────────────┘     │   │                   │
│   │   │                │                     │   │                   │
│   │   │                ▼                     │   │                   │
│   │   │   ┌────────────────────────────┐     │   │                   │
│   │   │   │   PostgreSQL 16 (1 pod)    │     │   │                   │
│   │   │   │   PVC 1Gi persistente      │     │   │                   │
│   │   │   │   porta 5432 (ClusterIP)   │     │   │                   │
│   │   │   └────────────────────────────┘     │   │                   │
│   │   │                                      │   │                   │
│   │   └──────────────────────────────────────┘   │                   │
│   │                                              │                   │
│   │   NodePort :30080 ──► :8000                  │                   │
│   └──────────────────────────────────────────────┘                   │
│                                                                      │
│   Usuário ──► http://<EC2_IP>:30080                                  │
└──────────────────────────────────────────────────────────────────────┘
```

**Componentes e responsabilidades:**

| Componente | Papel |
|------------|-------|
| **GitHub** | Versionamento do código e dos manifests Kubernetes |
| **GitHub Actions** | Orquestra o pipeline CI/CD (build, push, deploy) |
| **Docker** | Empacota a aplicação em imagem reproduzível |
| **GHCR** | Armazena as imagens Docker versionadas por commit SHA |
| **k3s** | Distribuição leve do Kubernetes que roda no EC2 |
| **PostgreSQL** | Persistência de dados com volume Kubernetes |
| **AWS EC2** | Infraestrutura cloud onde o cluster é executado |

---

## 3. Stack de Tecnologias

| Categoria | Tecnologia | Função |
|-----------|-----------|--------|
| **Linguagem** | Python 3.12 | Runtime da aplicação |
| **Framework** | FastAPI (async) | API REST de alta performance |
| **Banco de Dados** | PostgreSQL 16 + SQLAlchemy async + asyncpg | Persistência com queries assíncronas |
| **Containerização** | Docker (multi-stage build) | Empacotamento e isolamento da aplicação |
| **Orquestração** | Kubernetes (k3s) | Gerenciamento de containers em produção |
| **CI/CD** | GitHub Actions | Automação do pipeline de entrega |
| **Registry** | GitHub Container Registry (GHCR) | Armazenamento de imagens Docker |
| **Monitoramento** | Prometheus (prometheus-fastapi-instrumentator) | Coleta de métricas da aplicação |
| **Cloud** | AWS EC2 (Ubuntu 22.04) | Hospedagem do cluster Kubernetes |
| **Versionamento** | Git + GitHub | Controle de código e colaboração |

---

## 4. Pipeline CI/CD

O pipeline é definido em `.github/workflows/deploy.yml` e executa automaticamente a cada push na branch `main`.

### Trigger

```yaml
on:
  push:
    branches: [main]
```

### Etapas do Pipeline

```
Checkout ──► Login GHCR ──► Build + Push ──► Copia manifests ──► Deploy na EC2
```

**1. Checkout do código**
O GitHub Actions clona o repositório na máquina virtual do runner usando `actions/checkout@v4`.

**2. Autenticação no GHCR**
Realiza login no GitHub Container Registry utilizando o `GITHUB_TOKEN` gerado automaticamente, sem necessidade de credenciais adicionais.

**3. Build e Push da imagem Docker**
Constrói a imagem usando `docker/build-push-action@v6` e publica no GHCR com duas tags:
- `ghcr.io/<owner>/orderservice-projectdevops:<commit-sha>` — versionamento imutável
- `ghcr.io/<owner>/orderservice-projectdevops:latest` — referência para a versão mais recente

**4. Copia manifests para a EC2**
Transfere o diretório `k8s/` via SCP para a instância EC2, garantindo que os manifests estejam atualizados.

**5. Deploy no Kubernetes**
Conecta na EC2 via SSH e executa:
- Substituição de placeholders nos manifests (`__GITHUB_USER__`, `__IMAGE_NAME__`, `__DB_PASSWORD__`)
- `kubectl apply` em todos os manifests (namespace, secrets, volumes, deployments, services)
- `kubectl set image` para atualizar a imagem do deployment com o SHA do commit
- `kubectl rollout status` para aguardar a conclusão do deploy (timeout: 120s)

### Secrets necessários

| Secret | Descrição |
|--------|-----------|
| `EC2_HOST` | Elastic IP da instância EC2 |
| `EC2_SSH_KEY` | Chave privada SSH (conteúdo do `.pem`) |
| `DB_PASSWORD` | Senha do PostgreSQL para o cluster |

> O `GITHUB_TOKEN` é provido automaticamente pelo GitHub Actions com permissões de `contents: read` e `packages: write`.

---

## 5. Docker

### Containerização da aplicação

A aplicação é empacotada usando um **Dockerfile multi-stage**, que separa o ambiente de build do ambiente de execução:

```dockerfile
# Stage 1: instala dependências em um ambiente de build
FROM python:3.12-slim AS builder
WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: copia apenas os artefatos necessários para a imagem final
FROM python:3.12-slim
WORKDIR /project
COPY --from=builder /install /usr/local
COPY app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Benefícios da abordagem

- **Imagem leve** — a imagem final não contém ferramentas de build, headers de compilação ou cache do pip
- **Reprodutibilidade** — o mesmo Dockerfile gera imagens idênticas em qualquer ambiente
- **Portabilidade** — a imagem roda em qualquer host com Docker, do laptop do desenvolvedor ao cluster Kubernetes
- **Segurança** — superfície de ataque reduzida por não incluir pacotes desnecessários

### Desenvolvimento local com Docker Compose

O `docker-compose.yml` orquestra a aplicação junto com o PostgreSQL para desenvolvimento:

```bash
docker compose up    # sobe app + banco
docker compose down  # derruba tudo
```

---

## 6. Deploy com Kubernetes

A aplicação roda em um cluster **k3s** com os seguintes recursos Kubernetes:

### Deployment — order-service

- **2 réplicas** — garante alta disponibilidade; se um pod falhar, o outro continua servindo
- **Liveness probe** — verifica `/health` a cada 15s. Se falhar, o Kubernetes **reinicia o pod automaticamente** (self-healing)
- **Readiness probe** — verifica `/health` a cada 10s. Pods que não estão prontos são **removidos do balanceamento** até se recuperarem
- **Resource limits** — cada pod tem limites definidos (CPU: 250m, memória: 256Mi), impedindo que um container monopolize recursos do nó
- **Credenciais via Secret** — usuário, senha e nome do banco são injetados via `secretKeyRef`, sem hardcoding nos manifests

### Deployment — PostgreSQL

- **1 réplica** com `PersistentVolumeClaim` de 1Gi — dados sobrevivem a reinícios e recriações do pod
- Acessível apenas internamente via **ClusterIP** na porta 5432

### Service — NodePort

A aplicação é exposta externamente através de um **Service NodePort** na porta `30080`:

```
Usuário ──► EC2_IP:30080 ──► Service (NodePort) ──► Pod :8000
```

Qualquer requisição na porta 30080 do EC2 é roteada para um dos pods da aplicação na porta 8000.

### Self-healing e resiliência

O Kubernetes monitora continuamente o estado dos pods. Se um pod falhar ou não responder ao liveness probe:

1. O pod é automaticamente reiniciado
2. O tráfego é redirecionado para os pods saudáveis
3. O deployment garante que sempre existam 2 réplicas rodando

---

## 7. Ambiente de Deploy

### Infraestrutura

O cluster Kubernetes roda em uma **instância AWS EC2** com a seguinte configuração:

| Especificação | Valor |
|---------------|-------|
| **Sistema Operacional** | Ubuntu 22.04 LTS |
| **Tipo de instância** | t3.small (mínimo recomendado) |
| **Distribuição Kubernetes** | k3s (leve, single-node) |
| **IP** | Elastic IP fixo |
| **Portas abertas** | 22 (SSH), 30080 (aplicação), 6443 (API Kubernetes) |

### Deploy real em produção

Este **não é um projeto que roda apenas localmente**. A aplicação está configurada para deploy em um cluster Kubernetes real na AWS, acessível publicamente pela internet.

O script `scripts/setup-ec2.sh` automatiza toda a preparação do servidor:
1. Atualiza o sistema operacional
2. Instala o k3s e configura o `kubectl`
3. Cria o pull secret para autenticação no GHCR
4. Substitui placeholders nos manifests
5. Aplica todos os manifests Kubernetes
6. Aguarda os deployments ficarem prontos

Após a execução do setup, o pipeline CI/CD assume: qualquer push na `main` atualiza a aplicação automaticamente.

---

## 8. Como Executar Localmente

### Pré-requisitos

- **Docker** e **Docker Compose** instalados

### Opção 1 — Docker Compose (recomendado)

Sobe a aplicação e o PostgreSQL com um único comando:

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/Projeto-devops.git
cd Projeto-devops

# (Opcional) Configurar variáveis de ambiente
cp .env.example .env

# Subir os serviços
docker compose up
```

Acesse:
- **Dashboard:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Métricas:** http://localhost:8000/metrics
- **Health check:** http://localhost:8000/health

### Opção 2 — Docker (imagem avulsa)

Para quando você já possui um PostgreSQL rodando:

```bash
# Build da imagem
docker build -t order-service .

# Rodar o container
docker run -p 8000:8000 \
  -e DATABASE_HOST=host.docker.internal \
  -e DATABASE_USER=orders \
  -e DATABASE_PASSWORD=orders \
  -e DATABASE_NAME=orders \
  order-service
```

### Gerar tráfego de teste

```bash
bash scripts/traffic.sh http://localhost:8000
```

---

## 9. Fluxo de Deploy

O que acontece automaticamente após um `git push origin main`:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. TRIGGER         git push na branch main                     │
│       │                                                         │
│       ▼                                                         │
│  2. BUILD           GitHub Actions constrói a imagem Docker     │
│       │             usando o Dockerfile multi-stage             │
│       ▼                                                         │
│  3. PUSH            Imagem é publicada no GHCR com tag          │
│       │             do commit SHA (versionamento imutável)      │
│       ▼                                                         │
│  4. TRANSFER        Manifests K8s são copiados via SCP          │
│       │             para a instância EC2                        │
│       ▼                                                         │
│  5. DEPLOY          Via SSH, os manifests são aplicados         │
│       │             e a imagem é atualizada com kubectl         │
│       ▼                                                         │
│  6. ROLLOUT         Kubernetes faz rolling update dos pods      │
│       │             sem downtime (2 réplicas alternadas)        │
│       ▼                                                         │
│  7. VERIFICAÇÃO     kubectl rollout status aguarda              │
│                     confirmação de deploy bem-sucedido          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Tempo médio:** o pipeline completo executa em aproximadamente 2-3 minutos, do push à aplicação rodando em produção.

---

## 10. Estrutura do Projeto

```
.
├── app/                            # Código da aplicação
│   ├── main.py                     # Entrypoint FastAPI (lifespan, rotas, background tasks)
│   ├── routes.py                   # Endpoints CRUD para /orders
│   ├── models.py                   # Schemas Pydantic (validação de entrada/saída)
│   ├── database.py                 # Engine async SQLAlchemy + gerenciamento de sessão
│   ├── db_models.py                # Modelo ORM mapeando a tabela orders
│   ├── metrics.py                  # Configuração do Prometheus
│   ├── dashboard.py                # HTML do dashboard interativo (/)
│   ├── docs_page.py                # HTML do Swagger UI customizado (/docs)
│   └── requirements.txt            # Dependências Python
│
├── k8s/                            # Manifests Kubernetes
│   ├── namespace.yaml              # Namespace order-service
│   ├── postgres-secret.yaml        # Credenciais do banco (com placeholder)
│   ├── postgres-pvc.yaml           # Volume persistente de 1Gi
│   ├── postgres-deployment.yaml    # Deployment do PostgreSQL 16
│   ├── postgres-service.yaml       # Service ClusterIP para o banco
│   ├── deployment.yaml             # Deployment da aplicação (2 réplicas, probes, limits)
│   └── service.yaml                # Service NodePort na porta 30080
│
├── scripts/
│   ├── setup-ec2.sh                # Script de provisionamento do EC2 (k3s + manifests)
│   └── traffic.sh                  # Gerador de tráfego para testes
│
├── .github/workflows/
│   └── deploy.yml                  # Pipeline CI/CD (GitHub Actions)
│
├── Dockerfile                      # Multi-stage build (builder + runtime)
├── docker-compose.yml              # Stack local (app + PostgreSQL)
├── .env.example                    # Template de variáveis de ambiente
└── CLAUDE.md                       # Documentação técnica do projeto
```

---

## 11. Melhorias Futuras

| Melhoria | Descrição |
|----------|-----------|
| **Observabilidade completa** | Integrar Grafana para dashboards visuais sobre as métricas Prometheus já coletadas |
| **Auto scaling (HPA)** | Configurar Horizontal Pod Autoscaler para escalar réplicas baseado em CPU/memória |
| **Ingress Controller** | Substituir NodePort por Ingress com NGINX para roteamento HTTP e terminação TLS |
| **Certificado SSL** | Adicionar cert-manager + Let's Encrypt para HTTPS automático |
| **Testes automatizados no pipeline** | Incluir etapa de testes unitários e de integração antes do build |
| **Ambientes separados** | Criar namespaces para staging e produção com promoção controlada |
| **Infrastructure as Code** | Provisionar a EC2 com Terraform em vez de setup manual |
| **GitOps com ArgoCD** | Substituir o deploy via SSH por reconciliação declarativa com ArgoCD |
| **Alertas** | Configurar Alertmanager para notificações em caso de falha nos pods ou métricas anômalas |

---

## 12. Conclusão

Este projeto demonstra a implementação prática de um **pipeline DevOps completo**, abrangendo:

- **Integração Contínua** — cada push dispara build e publicação automatizados via GitHub Actions
- **Entrega Contínua** — o deploy acontece automaticamente no cluster Kubernetes após o push
- **Containerização** — aplicação empacotada em imagem Docker otimizada com multi-stage build
- **Orquestração** — Kubernetes gerencia réplicas, self-healing, probes e rolling updates
- **Deploy em Cloud** — cluster k3s real rodando em instância AWS EC2, acessível publicamente
- **Observabilidade** — métricas Prometheus e health checks integrados desde o início

O objetivo é mostrar domínio sobre o ciclo completo de entrega de software, desde o commit até a aplicação rodando em produção, com automação, reprodutibilidade e boas práticas de engenharia.

---

Desenvolvido por **Matheus Santos Caldas**
