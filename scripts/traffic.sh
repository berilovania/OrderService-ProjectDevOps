#!/bin/bash
# traffic.sh — Gera tráfego realista contra o Order Service
# Usage: bash scripts/traffic.sh [OPTIONS] [BASE_URL]
#
# Options:
#   --loop, -l         Roda em loop contínuo (Ctrl+C para parar)
#   --interval, -i N   Segundos entre ciclos no loop (padrão: 5)
#   --count, -n N      Número de ciclos no loop (padrão: infinito)
#   --orders, -o N     Pedidos criados por ciclo (padrão: 2, máx: 6)
#   --quiet, -q        Saída reduzida (só mostra resumo por ciclo)

# --- Dados realistas (espelhando app/dashboard.py) ---
CUSTOMERS=("João Silva" "Maria Santos" "Pedro Costa" "Ana Oliveira" "Carlos Souza" "Beatriz Lima")
ITEMS_LIST=(
  "Notebook Pro,Mouse Gamer"
  "Teclado Mecânico,Monitor 27in"
  "Webcam Full HD,Headset BT"
  "SSD NVMe 1TB,Hub USB-C"
  "Mousepad XL,Suporte Notebook"
  "Cadeira Gamer,Mesa Articulada"
)

# --- Defaults ---
LOOP=false
INTERVAL=5
COUNT=0        # 0 = infinito
ORDERS_PER_CYCLE=2
QUIET=false
BASE_URL="http://localhost:8000"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --loop|-l)    LOOP=true; shift ;;
    --quiet|-q)   QUIET=true; shift ;;
    --interval|-i) INTERVAL="$2"; shift 2 ;;
    --count|-n)   COUNT="$2"; shift 2 ;;
    --orders|-o)  ORDERS_PER_CYCLE="$2"; shift 2 ;;
    http://*|https://*) BASE_URL="$1"; shift ;;
    *)            echo "Opção desconhecida: $1"; exit 1 ;;
  esac
done

# Limita orders ao máximo de 6 (tamanho dos arrays)
[[ $ORDERS_PER_CYCLE -gt 6 ]] && ORDERS_PER_CYCLE=6

# --- Estado global ---
cycle=0
total_created=0

# --- Sinal de interrupção ---
trap 'echo -e "\n==> Interrompido após $cycle ciclos. Total de pedidos criados: $total_created"; exit 0' INT

# --- Funções auxiliares ---

random_total() {
  awk "BEGIN{printf \"%.2f\", 80 + ($RANDOM % 1500) + $RANDOM/32768}"
}

# Converte array CSV de itens para JSON array
items_to_json() {
  local csv="$1"
  local json="["
  IFS=',' read -ra parts <<< "$csv"
  for i in "${!parts[@]}"; do
    [[ $i -gt 0 ]] && json+=","
    json+="\"${parts[$i]}\""
  done
  json+="]"
  echo "$json"
}

log() {
  $QUIET || echo "$@"
}

run_cycle() {
  local created_ids=()
  local created=0
  local completed=0
  local cancelled=0

  # 1. Criar pedidos
  log -e "\n--- Criando $ORDERS_PER_CYCLE pedidos ---"
  for ((i=0; i<ORDERS_PER_CYCLE; i++)); do
    local idx=$(( RANDOM % 6 ))
    local customer="${CUSTOMERS[$idx]}"
    local items_csv="${ITEMS_LIST[$idx]}"
    local items_json
    items_json=$(items_to_json "$items_csv")
    local total
    total=$(random_total)

    local payload="{\"customer\": \"${customer}\", \"items\": ${items_json}, \"total\": ${total}}"
    local response
    response=$(curl -s -X POST "${BASE_URL}/orders" \
      -H "Content-Type: application/json" \
      -d "$payload")

    local order_id
    order_id=$(echo "$response" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)

    if [[ -n "$order_id" ]]; then
      created_ids+=("$order_id")
      created=$((created + 1))
      log "  + Pedido criado: ${order_id} | ${customer} | R\$ ${total}"
    else
      log "  ! Falha ao criar pedido"
    fi
  done

  total_created=$((total_created + created))

  # 2. Avançar ciclo de vida: created → processing → completed
  log -e "\n--- Atualizando status ---"
  for order_id in "${created_ids[@]}"; do
    curl -s -X PATCH "${BASE_URL}/orders/${order_id}/status" \
      -H "Content-Type: application/json" \
      -d '{"status": "processing"}' > /dev/null

    curl -s -X PATCH "${BASE_URL}/orders/${order_id}/status" \
      -H "Content-Type: application/json" \
      -d '{"status": "completed"}' > /dev/null

    completed=$((completed + 1))
    log "  ✓ ${order_id} → processing → completed"
  done

  # 3. Cancelar um pedido aleatório (1 em 3 ciclos)
  if [[ $(( cycle % 3 )) -eq 0 ]] && [[ ${#created_ids[@]} -gt 0 ]]; then
    local cancel_idx=$(( RANDOM % ${#created_ids[@]} ))
    local cancel_id="${created_ids[$cancel_idx]}"
    local cancel_resp
    cancel_resp=$(curl -s -X DELETE "${BASE_URL}/orders/${cancel_id}")
    cancelled=$((cancelled + 1))
    log "  ✗ ${cancel_id} cancelado"
  fi

  # 4. Resumo do ciclo
  local ts
  ts=$(date "+%Y-%m-%d %H:%M:%S")
  if $QUIET; then
    echo "[${ts}] Ciclo #${cycle} — ${created} criados, ${completed} concluídos, ${cancelled} cancelados"
  else
    echo -e "\n==> Ciclo #${cycle} concluído — ${created} criados, ${completed} concluídos, ${cancelled} cancelados"
  fi
}

# --- Execução ---

if ! $QUIET; then
  echo "==> Targeting: ${BASE_URL}"
  echo -e "\n--- Health Check ---"
  curl -s "${BASE_URL}/health" | python -m json.tool
fi

if $LOOP; then
  while true; do
    cycle=$((cycle + 1))
    run_cycle

    if [[ $COUNT -gt 0 ]] && [[ $cycle -ge $COUNT ]]; then
      echo -e "\n==> $COUNT ciclos concluídos. Total de pedidos criados: $total_created"
      break
    fi

    sleep "$INTERVAL"
  done
else
  # Modo único: 1 ciclo com saída completa
  cycle=1
  ORDERS_PER_CYCLE=3
  run_cycle

  log -e "\n--- Estado Final ---"
  $QUIET || curl -s "${BASE_URL}/orders" | python -m json.tool

  log -e "\n--- Métricas (primeiras 20 linhas) ---"
  $QUIET || curl -s "${BASE_URL}/metrics" | head -20

  echo -e "\n==> Concluído! Total de pedidos criados: $total_created"
fi
