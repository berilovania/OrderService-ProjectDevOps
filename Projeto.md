# Planejamento Técnico – Projeto DevOps Completo

## Objetivo

Construir um pipeline DevOps completo, automatizado e funcional, integrando versionamento de código, containerização, integração contínua, entrega contínua e deploy em ambiente real utilizando Kubernetes.

O projeto tem como foco validar habilidades práticas em:

* CI/CD
* Docker
* Kubernetes
* Deploy em cloud (AWS EC2)
* Integração com GitHub

Não há foco em testes automatizados neste momento.

---

## Arquitetura Geral

O fluxo do sistema seguirá o seguinte pipeline:

Código versionado no GitHub → Execução de pipeline CI/CD → Build da aplicação → Criação de imagem Docker → Push para Container Registry → Deploy automático em cluster Kubernetes → Aplicação em execução em ambiente real

---

## Controle de Versão

O repositório será hospedado no GitHub, contendo:

* Código da aplicação
* Dockerfile
* Arquivos de configuração do Kubernetes (manifests)
* Configuração do pipeline CI/CD (GitHub Actions)
* Documentação completa no README

A estratégia de versionamento seguirá:

* Branch principal: main
* Uso de commits semânticos (feat, fix, chore)
* Possível uso de versionamento de imagens baseado em hash de commit

---

## Pipeline CI/CD

O pipeline será implementado utilizando GitHub Actions e será acionado automaticamente a cada push na branch principal.

### Etapas do pipeline:

1. Checkout do código
2. Build da aplicação
3. Build da imagem Docker
4. Tag da imagem (preferencialmente com hash do commit)
5. Push da imagem para o container registry
6. Autenticação no cluster Kubernetes
7. Deploy automático utilizando kubectl

### Requisitos:

* Uso de secrets no GitHub para credenciais (Docker e Kubernetes)
* Pipeline totalmente automatizado (sem intervenção manual)

---

## Containerização (Docker)

A aplicação será containerizada utilizando Docker, garantindo padronização do ambiente de execução.

### Requisitos:

* Dockerfile otimizado (imagem base leve)
* Uso de .dockerignore
* Build reproduzível
* Execução da aplicação dentro do container

---

## Container Registry

A imagem Docker será armazenada em um registry, podendo ser:

* Docker Hub
* GitHub Container Registry

### Estratégia:

* Versionamento de imagens por tag (latest e commit hash)
* Atualização automática via pipeline

---

## Orquestração com Kubernetes

A aplicação será implantada em um cluster Kubernetes rodando em uma instância EC2.

### Componentes obrigatórios:

* Deployment (gerenciamento de pods)
* Service (exposição da aplicação)
* Configuração de replicas (mínimo 2)

### Opcional (recomendado):

* Ingress para roteamento HTTP

### Deploy:

* Utilização de arquivos YAML versionados no repositório
* Deploy automatizado via pipeline (kubectl apply)

---

## Ambiente de Deploy (AWS EC2)

O cluster Kubernetes será configurado manualmente em uma instância EC2.

### Configuração mínima:

* Sistema operacional Linux (Ubuntu Server)
* Docker instalado
* Kubernetes instalado (k3s, kubeadm ou similar)
* Acesso via SSH com chave
* Configuração de portas via Security Group

### Objetivo:

Simular ambiente real de produção, sem uso de serviços gerenciados.

---

## Fluxo de Deploy

1. Desenvolvedor realiza commit
2. Código é enviado para o GitHub
3. Pipeline CI/CD é acionado automaticamente
4. Imagem Docker é construída
5. Imagem é enviada para o registry
6. Pipeline conecta ao cluster Kubernetes
7. Deployment é atualizado
8. Nova versão da aplicação é disponibilizada automaticamente

---

## Documentação

O projeto deverá conter um README detalhado com:

* Descrição da arquitetura
* Explicação do pipeline CI/CD
* Instruções para execução local
* Instruções de deploy
* Estrutura do projeto
* Prints ou exemplos de execução

---

## Considerações Finais

O projeto tem como objetivo demonstrar domínio prático de um fluxo DevOps completo, com foco em automação, deploy contínuo e execução em ambiente real.
A aplicação em si será utilizada apenas como meio para validação da arquitetura, sendo o foco principal a infraestrutura, pipeline e integração entre as ferramentas.

Ainda não existe uma aplicaçao em mente mas planeje qual melhor se encaixa nesses criterios:
* gere tráfego 
* tenha comportamento
* tenha métricas interessantes
* simule um sistema real
* quero algo simples, mas que parece real