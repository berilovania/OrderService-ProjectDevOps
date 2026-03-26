# Order Service — Pipeline DevOps Completo

Pipeline CI/CD de ponta a ponta com containerização Docker, orquestração Kubernetes e deploy automatizado em nuvem GCP. Do `git push` à produção em minutos, sem intervenção manual.

---

## 1. Visão Geral do Projeto

Este projeto implementa um **pipeline DevOps completo e funcional**, cobrindo todas as etapas do ciclo de vida de entrega de software: versionamento, integração contínua, containerização, registro de imagens, orquestração e deploy automatizado em ambiente cloud real.

A aplicação — uma API REST de gerenciamento de pedidos construída com FastAPI — serve como **carga de trabalho para validar a infraestrutura**. O foco do projeto não está na lógica de negócio, mas sim na demonstração prática de:

- **Automação completa** — zero intervenção manual entre o commit e a produção
- **Infraestrutura como código** — manifests Kubernetes versionados no repositório
- **Deploy real em nuvem** — cluster Kubernetes rodando em VM GCP Compute Engine
- **Boas práticas de containerização** — imagem Docker otimizada com multi-stage build
- **Observabilidade** — métricas Prometheus, dashboards Grafana, health checks e probes de liveness/readiness
- **Segurança em camadas** — container não-root, securityContext, scan de vulnerabilidades Trivy
- **HTTPS automático** — TLS via cert-manager + Let's Encrypt, renovação automática, domínio customizado

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
│   │  4. Copia manifests para GCP (SCP)  │                            │
│   │  5. Deploy via SSH + kubectl        │                            │
│   └──────────────────┬──────────────────┘                            │
│                      │                                               │
│                      ▼                                               │
│   ┌──────────────────────────────────────────────┐                   │
│   │       GCP Compute Engine (Ubuntu 22.04)      │                   │
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
│   │   │   │   PostgreSQL 16 (Stateful) │     │   │                   │
│   │   │   │   PVC 1Gi persistente      │     │   │                   │
│   │   │   │   porta 5432 (Headless)    │     │   │                   │
│   │   │   │                            │     │   │                   │
│   │   │   └────────────────────────────┘     │   │                   │
│   │   │                                      │   │                   │
│   │   └──────────────────────────────────────┘   │                   │
│   │                                              │                   │
│   │   NodePort :30080 ──► :8000  (acesso direto) │                   │
│   │   NGINX Ingress :80/:443 ──► :8000           │                   │
│   └──────────────────────────────────────────────┘                   │
│                                                                      │
│   Usuário ──► https://<DOMINIO>       (HTTPS via cert-manager)       │
│   Usuário ──► http://<GCP_IP>:30080   (NodePort direto)              │
└──────────────────────────────────────────────────────────────────────┘
```

**Componentes e responsabilidades:**

| Componente | Papel |
|------------|-------|
| **GitHub** | Versionamento do código e dos manifests Kubernetes |
| **GitHub Actions** | Orquestra o pipeline CI/CD (build, push, deploy) |
| **Docker** | Empacota a aplicação em imagem reproduzível |
| **GHCR** | Armazena as imagens Docker versionadas por commit SHA |
| **k3s** | Distribuição leve do Kubernetes que roda na VM GCP |
| **PostgreSQL** | Persistência de dados com volume Kubernetes |
| **NGINX Ingress Controller** | Roteamento HTTP/HTTPS com rate-limiting e TLS termination |
| **cert-manager + Let's Encrypt** | Provisionamento e renovação automática de certificados TLS |
| **GCP Compute Engine** | Infraestrutura cloud onde o cluster é executado |

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
| **Dashboards** | Grafana | Visualização de métricas com datasource Prometheus auto-provisionado |
| **Ingress** | NGINX Ingress Controller | Roteamento HTTP/HTTPS, rate-limiting, TLS termination |
| **TLS** | cert-manager + Let's Encrypt (HTTP-01) | Certificados automáticos com renovação sem intervenção manual |
| **Cloud** | GCP Compute Engine (Ubuntu 22.04) | Hospedagem do cluster Kubernetes |
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

### Jobs do Pipeline

```
[test] ──► [build-and-scan] ──► [deploy]
```

O pipeline é dividido em três jobs com dependência sequencial — o deploy só ocorre se os testes passarem e a imagem for aprovada no scan de segurança.

**Job 1 — test**

Executa os testes automatizados contra um banco PostgreSQL real (service container no runner):
- Setup do Python 3.12 e instalação das dependências de produção + desenvolvimento
- Executa `pytest` com banco PostgreSQL 16 em container (`localhost:5432`)
- Falha imediata se qualquer teste quebrar — nenhuma imagem é construída

**Job 2 — build-and-scan**

Constrói e verifica a segurança da imagem antes de publicá-la:
- Constrói a imagem Docker com `docker/build-push-action@v6`
- **Trivy vulnerability scan** — analisa a imagem e falha em vulnerabilidades CRITICAL/HIGH com correção disponível
- Autentica no GHCR via `GITHUB_TOKEN` (sem credenciais adicionais)
- Publica a imagem com duas tags:
  - `ghcr.io/<owner>/orderservice-projectdevops:<commit-sha>` — versionamento imutável
  - `ghcr.io/<owner>/orderservice-projectdevops:latest` — referência para a versão mais recente

**Job 3 — deploy**

Aplica a nova versão no cluster Kubernetes:
- Copia os manifests `k8s/` via SCP para a VM GCP
- Conecta na VM GCP via SSH e executa:
  - Criação/atualização do Secret (credenciais PostgreSQL, direto no cluster, sem gravar em disco)
  - Substituição de placeholders nos manifests (`__GITHUB_USER__`, `__IMAGE_NAME__`, `__DOMAIN__`, `__ACME_EMAIL__`)
  - `kubectl apply` em todos os manifests com validação habilitada
  - Aguarda o StatefulSet do PostgreSQL ficar pronto (timeout: 180s)
  - `kubectl set image` para atualizar a imagem do deployment com o SHA do commit
  - `kubectl rollout status` para aguardar o rolling update (timeout: 600s)
  - Em caso de falha: imprime diagnóstico automático (status dos pods, eventos, logs)

### Secrets necessários

| Secret | Descrição |
|--------|-----------|
| `GCP_HOST` | External IP da VM GCP |
| `GCP_SSH_KEY` | Chave privada SSH |
| `DB_PASSWORD` | Senha do PostgreSQL para o cluster |
| `DOMAIN` | Domínio do serviço (ex: `order-service.matheuscaldas.com`) |
| `ACME_EMAIL` | Email para notificações Let's Encrypt |

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

# Usuário não-privilegiado (UID 1000 alinhado com securityContext do k8s)
RUN addgroup --system --gid 1000 app && adduser --system --uid 1000 --ingroup app app
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Benefícios da abordagem

- **Imagem leve** — a imagem final não contém ferramentas de build, headers de compilação ou cache do pip
- **Reprodutibilidade** — o mesmo Dockerfile gera imagens idênticas em qualquer ambiente
- **Portabilidade** — a imagem roda em qualquer host com Docker, do laptop do desenvolvedor ao cluster Kubernetes
- **Segurança** — container roda como usuário não-root (`app`, UID 1000), superfície de ataque reduzida

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
- **Resource limits** — cada pod tem limites definidos (CPU: 300m, memória: 192Mi), impedindo que um container monopolize recursos do nó
- **Credenciais via Secret** — usuário, senha e nome do banco são injetados via `secretKeyRef`, sem hardcoding nos manifests
- **SecurityContext** — container roda como usuário não-root (UID 1000), filesystem read-only, sem privilege escalation, todas as capabilities Linux removidas

### StatefulSet — PostgreSQL

- **StatefulSet** (em vez de Deployment) — garante identidade estável do pod e gerenciamento seguro de storage para workloads stateful
- **1 réplica** com `PersistentVolumeClaim` de 1Gi — dados sobrevivem a reinícios e recriações do pod
- Acessível apenas internamente via **Headless Service** (`clusterIP: None`) na porta 5432
- Limites de recursos ajustados para e2-small (2GB RAM): CPU 300m, memória 256Mi
- **SecurityContext** — `allowPrivilegeEscalation: false`

### Service — NodePort + Ingress HTTPS

A aplicação é exposta de duas formas:

```
# Via domínio (produção)
Usuário ──► https://<DOMINIO> ──► NGINX Ingress (:443) ──► Pod :8000

# Via NodePort (acesso direto / debug)
Usuário ──► GCP_IP:30080 ──► Service (NodePort) ──► Pod :8000
```

O **NGINX Ingress Controller** (`k8s/ingress.yaml`) gerencia:
- Rate-limiting: 10 req/s (burst até 30)
- Redirect HTTP → HTTPS automático (308)
- TLS termination com certificado Let's Encrypt (renovado automaticamente pelo cert-manager)
- Bloqueio do endpoint `/metrics` a nível de Ingress

O **cert-manager** (`k8s/clusterissuer.yaml`) provisiona certificados via ACME HTTP-01 com o Let's Encrypt production. O certificado é armazenado no Secret `order-service-tls` e renovado automaticamente antes do vencimento.

### Self-healing e resiliência

O Kubernetes monitora continuamente o estado dos pods. Se um pod falhar ou não responder ao liveness probe:

1. O pod é automaticamente reiniciado
2. O tráfego é redirecionado para os pods saudáveis
3. O deployment garante que sempre existam 2 réplicas rodando

---

## 7. Ambiente de Deploy

### Infraestrutura

O cluster Kubernetes roda em uma **VM GCP Compute Engine** com a seguinte configuração:

| Especificação | Valor |
|---------------|-------|
| **Sistema Operacional** | Ubuntu 22.04 LTS |
| **Tipo de instância** | e2-small (2 vCPU shared, 2GB RAM) |
| **Distribuição Kubernetes** | k3s (leve, single-node) |
| **IP** | External IP (estático) |
| **Portas abertas** | 22 (SSH), 80 (HTTP/redirect), 443 (HTTPS), 30080 (NodePort direto), 6443 (API Kubernetes) |

### Deploy real em produção

Este **não é um projeto que roda apenas localmente**. A aplicação está configurada para deploy em um cluster Kubernetes real na GCP, acessível publicamente pela internet.

O script `scripts/setup-gcp.sh` automatiza toda a preparação do servidor:

```bash
bash scripts/setup-gcp.sh <GITHUB_USER> [IMAGE_NAME] [DB_PASSWORD] <DOMAIN> <ACME_EMAIL>
```

1. Atualiza o sistema operacional
2. Instala o k3s (com Traefik desabilitado) e configura o `kubectl`
3. Instala o NGINX Ingress Controller e habilita snippet annotations
4. Instala o cert-manager e aguarda o webhook estar pronto
5. Cria os secrets (GHCR, PostgreSQL)
6. Substitui placeholders nos manifests (`__GITHUB_USER__`, `__IMAGE_NAME__`, `__DOMAIN__`, `__ACME_EMAIL__`)
7. Aplica todos os manifests Kubernetes (incluindo ClusterIssuer e Ingress)
8. Aguarda os deployments ficarem prontos

Após a execução do setup, o pipeline CI/CD assume: qualquer push na `main` atualiza a aplicação automaticamente.

> **Pré-requisito:** apontar o A record do subdomínio para o External IP da VM GCP antes de rodar o script — necessário para o desafio HTTP-01 do Let's Encrypt.

---

## 8. Testes Automatizados

O projeto inclui testes de integração que rodam contra um banco PostgreSQL real — sem mocks — para garantir que a lógica da aplicação e as queries funcionam corretamente.

### Ferramentas

| Ferramenta | Versão | Função |
|------------|--------|--------|
| `pytest` | 8.2.0 | Runner de testes |
| `pytest-asyncio` | 0.23 | Suporte a testes assíncronos |
| `httpx` | 0.27.0 | Cliente HTTP assíncrono para testar endpoints |

### Executar localmente

```bash
# Instalar dependências de desenvolvimento
pip install -r app/requirements.txt -r app/requirements-dev.txt

# Subir o banco de dados
docker compose up postgres -d

# Executar os testes
pytest tests/ -v
```

### No pipeline CI/CD

Os testes são executados automaticamente no job `test` com um container PostgreSQL 16 provisionado pelo próprio GitHub Actions. O job de build **só inicia** após os testes passarem.

---

## 9. Segurança

O projeto aplica segurança em múltiplas camadas:

### API pública

Todos os endpoints (`POST`, `PATCH`, `DELETE`, `GET`) são públicos — sem autenticação por API key.

### HTTPS / TLS

Todo o tráfego externo passa por HTTPS. O certificado TLS é emitido automaticamente pelo **cert-manager** via Let's Encrypt (HTTP-01) e renovado antes do vencimento sem intervenção manual. HTTP é redirecionado para HTTPS com `308 Permanent Redirect`.

### Métricas protegidas

O endpoint `/metrics` é protegido em duas camadas:
1. **Ingress** — bloqueado via `server-snippet` antes de chegar à aplicação
2. **Aplicação** — aceita apenas IPs internos (loopback / RFC1918) para acesso direto via NodePort

### Container não-root

A imagem Docker roda como usuário `app` (UID 1000), não como root. Isso limita o impacto de uma eventual vulnerabilidade no container.

### SecurityContext no Kubernetes

| Recurso | Configuração |
|---------|-------------|
| **order-service** | `runAsNonRoot: true`, `runAsUser: 1000`, `readOnlyRootFilesystem: true`, `drop ALL capabilities`, `allowPrivilegeEscalation: false` |
| **PostgreSQL** | `allowPrivilegeEscalation: false` |

### Proteção contra XSS

O dashboard interativo (`/`) utiliza construção DOM segura (`createElement` + `textContent`) em vez de `innerHTML` para renderizar dados vindos da API, prevenindo injeção de HTML/JavaScript malicioso.

### Scan de vulnerabilidades

Toda imagem Docker é analisada pelo **Trivy** no pipeline CI/CD. Vulnerabilidades `CRITICAL` ou `HIGH` com correção disponível **bloqueiam o deploy**.

---

## 10. Como Executar e Testar Localmente

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
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (usuário: `admin` / senha: `admin`)

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

## 11. Fluxo de Deploy

O que acontece automaticamente após um `git push origin main`:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. TRIGGER         git push na branch main                     │
│       │                                                         │
│       ▼                                                         │
│  2. TESTES          pytest contra PostgreSQL real               │
│       │             falha = pipeline interrompido               │
│       ▼                                                         │
│  3. BUILD           GitHub Actions constrói a imagem Docker     │
│       │             usando o Dockerfile multi-stage             │
│       ▼                                                         │
│  4. SCAN            Trivy analisa vulnerabilidades              │
│       │             falha em CVEs CRITICAL/HIGH corrigíveis     │
│       ▼                                                         │
│  5. PUSH            Imagem publicada no GHCR (tag: SHA)         │
│       │             versionamento imutável por commit           │
│       ▼                                                         │
│  6. TRANSFER        Manifests K8s copiados via SCP para GCP     │
│       │                                                         │
│       ▼                                                         │
│  7. DEPLOY          Via SSH: kubectl apply em todos os          │
│       │             manifests, kubectl set image                │
│       ▼                                                         │
│  8. ROLLOUT         Rolling update sem downtime (2 réplicas)    │
│       │             kubectl rollout status (timeout: 600s)      │
│       ▼                                                         │
│  9. DIAGNÓSTICO     Em caso de falha: logs e eventos            │
│                     impressos automaticamente                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Estrutura do Projeto

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
│   ├── requirements.txt            # Dependências de produção
│   └── requirements-dev.txt        # Dependências de desenvolvimento (pytest, httpx)
│
├── tests/                          # Testes de integração
│
├── k8s/                            # Manifests Kubernetes
│   ├── namespace.yaml              # Namespace order-service
│   ├── postgres-secret.yaml        # Credenciais do banco (placeholder __DB_PASSWORD__)
│   ├── postgres-pvc.yaml           # Volume persistente de 1Gi
│   ├── postgres-deployment.yaml    # StatefulSet do PostgreSQL 16 (1 réplica)
│   ├── postgres-service.yaml       # Headless Service na porta 5432
│   ├── deployment.yaml             # Deployment da aplicação (2 réplicas, probes, securityContext)
│   ├── service.yaml                # Service NodePort na porta 30080
│   ├── ingress.yaml                # Ingress NGINX com rate-limiting, TLS e bloqueio de /metrics
│   └── clusterissuer.yaml          # cert-manager ClusterIssuer (Let's Encrypt HTTP-01)
│
├── scripts/
│   ├── setup-gcp.sh                # Provisionamento da VM GCP (k3s + manifests)
│   ├── setup-ec2.sh                # Provisionamento de VM EC2 (k3s + manifests)
│   └── traffic.sh                  # Gerador de tráfego realista para testes
│
├── .github/workflows/
│   └── deploy.yml                  # Pipeline CI/CD (test → build+scan → deploy)
│
├── prometheus/
│   └── prometheus.yml              # Configuração do scrape do endpoint /metrics
│
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasource.yml      # Auto-provisionamento do datasource Prometheus
│
├── Dockerfile                      # Multi-stage build (builder + runtime)
├── docker-compose.yml              # Stack local (app + PostgreSQL + Prometheus + Grafana)
├── pytest.ini                      # Configuração do pytest
├── .env.example                    # Template de variáveis de ambiente
├── favicon.ico                     # Ícone customizado do serviço
└── CLAUDE.md                       # Documentação técnica do projeto
```

---

## 13. Melhorias Futuras

| Melhoria | Descrição |
|----------|-----------|
| **Auto scaling (HPA)** | Configurar Horizontal Pod Autoscaler para escalar réplicas baseado em CPU/memória |
| **Ambientes separados** | Criar namespaces para staging e produção com promoção controlada |
| **Infrastructure as Code** | Provisionar a VM GCP com Terraform em vez de setup manual |
| **GitOps com ArgoCD** | Substituir o deploy via SSH por reconciliação declarativa com ArgoCD |
| **Alertas** | Configurar Alertmanager para notificações em caso de falha nos pods ou métricas anômalas |
| **NetworkPolicy** | Restringir comunicação entre pods — permitir apenas order-service → postgres |

---

## 14. Troubleshooting

### k3s API não responde (`TLS handshake timeout` / `connection refused`)

Sintoma: `kubectl get pods` retorna erro de TLS ou conexão recusada, mesmo com k3s ativo.

**Causa:** instâncias com pouca RAM (1GB) ficam sem memória e o API server do k3s para de responder.

**Diagnóstico:**
```bash
sudo systemctl status k3s
free -h
```

Sinais de alerta: `swap > 400MB usado`, `load average > 2.0`, `%wa (I/O wait) > 50%` no `top`.

**Solução — reiniciar limpo:**
```bash
sudo k3s-killall.sh
sleep 15
sudo systemctl restart k3s
sleep 30
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
kubectl get nodes
```

---

### Limpeza completa da VM GCP

Use quando quiser reinstalar tudo do zero:

```bash
# 1. Parar todos os containers e desinstalar o k3s
sudo k3s-killall.sh
sudo /usr/local/bin/k3s-uninstall.sh

# 2. Remover dados residuais
sudo rm -rf /var/lib/rancher
sudo rm -rf /etc/rancher
sudo rm -rf ~/.kube
rm -rf ~/order-service

# 3. Verificar que ficou limpo (não deve retornar nenhum processo)
ps aux | grep k3s | grep -v grep
free -h
```

Após a limpeza, a memória deve estar com ~300MB usados e swap próximo de zero. Então refaça o setup:

```bash
git clone https://github.com/<GITHUB_USER>/OrderService-ProjectDevOps.git ~/order-service
cd ~/order-service
bash scripts/setup-gcp.sh <GITHUB_USER>
```

---

### Pipeline falha com `error validating data: ... TLS handshake timeout`

O `kubectl apply` tenta baixar o schema OpenAPI do cluster para validar os manifests, o que pode sobrecarregar o API server em instâncias com pouca RAM.

**Solução:** reiniciar o k3s para liberar memória (ver seção acima). O pipeline usa validação habilitada para garantir que manifests incorretos sejam detectados antes do deploy.

---

## 15. Conclusão

Este projeto demonstra a implementação prática de um **pipeline DevOps completo**, abrangendo:

- **Integração Contínua** — cada push dispara testes automáticos, scan de segurança, build e publicação via GitHub Actions
- **Entrega Contínua** — o deploy acontece automaticamente no cluster Kubernetes após testes e scan aprovados
- **Containerização** — aplicação empacotada em imagem Docker otimizada com multi-stage build
- **Orquestração** — Kubernetes gerencia réplicas, self-healing, probes e rolling updates
- **Persistência de dados** — PostgreSQL com PersistentVolumeClaim, dados sobrevivem a reinícios
- **Deploy em Cloud** — cluster k3s real rodando em VM GCP Compute Engine, acessível publicamente
- **Observabilidade** — métricas Prometheus e health checks integrados desde o início
- **Segurança em camadas** — containers não-root, securityContext restritivo, proteção contra XSS, scan Trivy em cada build, secrets sem hardcoding

O objetivo é mostrar domínio sobre o ciclo completo de entrega de software, desde o commit até a aplicação rodando em produção, com automação, reprodutibilidade e boas práticas de engenharia.

---

2026 — desenvolvido por **Matheus Santos**
