#!/bin/bash
# traffic.sh — Generate realistic traffic against the Order Service
# Usage: bash scripts/traffic.sh [OPTIONS] [BASE_URL]
#
# Options:
#   --loop, -l         Run in continuous loop (Ctrl+C to stop)
#   --interval, -i N   Seconds between cycles in loop mode (default: 5)
#   --count, -n N      Number of cycles in loop mode (default: infinite)
#   --orders, -o N     Orders created per cycle (default: 2, max: 6)
#   --quiet, -q        Reduced output (only shows cycle summary)

# --- Realistic data (mirroring app/dashboard.py) ---
CUSTOMERS=("John Silva" "Maria Santos" "Peter Costa" "Ana Oliveira" "Carlos Souza" "Beatriz Lima")
ITEMS_LIST=(
  "Notebook Pro,Gaming Mouse"
  "Mechanical Keyboard,27in Monitor"
  "Full HD Webcam,BT Headset"
  "SSD NVMe 1TB,USB-C Hub"
  "XL Mousepad,Laptop Stand"
  "Gaming Chair,Articulated Desk"
)

# --- Defaults ---
LOOP=false
INTERVAL=10
COUNT=0        # 0 = infinite
ORDERS_PER_CYCLE=4
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
    *)            echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Limit orders to array size (max 6)
[[ $ORDERS_PER_CYCLE -gt 6 ]] && ORDERS_PER_CYCLE=6

# --- Global state ---
cycle=0
total_created=0

# --- Interrupt handler ---
trap 'echo -e "\n==> Interrupted after $cycle cycles. Total orders created: $total_created"; exit 0' INT

# --- Helper functions ---

random_total() {
  awk "BEGIN{printf \"%.2f\", 80 + ($RANDOM % 1500) + $RANDOM/32768}"
}

# Convert CSV items array to JSON array
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

  # 1. Create orders
  log -e "\n--- Creating $ORDERS_PER_CYCLE orders ---"
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
    order_id=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)

    if [[ -n "$order_id" ]]; then
      created_ids+=("$order_id")
      created=$((created + 1))
      log "  + Order created: ${order_id} | ${customer} | \$ ${total}"
    else
      log "  ! Failed to create order"
    fi
  done

  total_created=$((total_created + created))

  # 2. Advance lifecycle: created → processing → (pause) → completed
  log -e "\n--- Updating status ---"
  for order_id in "${created_ids[@]}"; do
    curl -s -X PATCH "${BASE_URL}/orders/${order_id}/status" \
      -H "Content-Type: application/json" \
      -d '{"status": "processing"}' > /dev/null
    log "  … ${order_id} → processing"
  done

  # Pause to make "processing" status visible on dashboard
  sleep 4

  for order_id in "${created_ids[@]}"; do
    curl -s -X PATCH "${BASE_URL}/orders/${order_id}/status" \
      -H "Content-Type: application/json" \
      -d '{"status": "completed"}' > /dev/null
    completed=$((completed + 1))
    log "  ✓ ${order_id} → completed"
  done

  # 3. Cancel a random order (1 in 3 cycles)
  if [[ $(( cycle % 3 )) -eq 0 ]] && [[ ${#created_ids[@]} -gt 0 ]]; then
    local cancel_idx=$(( RANDOM % ${#created_ids[@]} ))
    local cancel_id="${created_ids[$cancel_idx]}"
    local cancel_resp
    cancel_resp=$(curl -s -X DELETE "${BASE_URL}/orders/${cancel_id}")
    cancelled=$((cancelled + 1))
    log "  ✗ ${cancel_id} cancelled"
  fi

  # 4. Cycle summary
  local ts
  ts=$(date "+%Y-%m-%d %H:%M:%S")
  if $QUIET; then
    echo "[${ts}] Cycle #${cycle} — ${created} created, ${completed} completed, ${cancelled} cancelled"
  else
    echo -e "\n==> Cycle #${cycle} done — ${created} created, ${completed} completed, ${cancelled} cancelled"
  fi
}

# --- Execution ---

if ! $QUIET; then
  echo "==> Targeting: ${BASE_URL}"
  echo -e "\n--- Health Check ---"
  curl -s "${BASE_URL}/health" | python3 -m json.tool
fi

if $LOOP; then
  while true; do
    cycle=$((cycle + 1))
    run_cycle

    if [[ $COUNT -gt 0 ]] && [[ $cycle -ge $COUNT ]]; then
      echo -e "\n==> $COUNT cycles completed. Total orders created: $total_created"
      break
    fi

    sleep "$INTERVAL"
  done
else
  # Single mode: 1 cycle with full output
  cycle=1
  ORDERS_PER_CYCLE=3
  run_cycle

  log -e "\n--- Final State ---"
  $QUIET || curl -s "${BASE_URL}/orders" | python3 -m json.tool

  log -e "\n--- Metrics (first 20 lines) ---"
  $QUIET || curl -s "${BASE_URL}/metrics" | head -20

  echo -e "\n==> Done! Total orders created: $total_created"
fi
