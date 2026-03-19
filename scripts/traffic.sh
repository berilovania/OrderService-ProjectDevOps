#!/bin/bash
# traffic.sh — Generate sample traffic against the Order Service
# Usage: bash scripts/traffic.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"

echo "==> Targeting: ${BASE_URL}"

# Health check
echo -e "\n--- Health Check ---"
curl -s "${BASE_URL}/health" | python -m json.tool

# Create orders
echo -e "\n--- Creating Orders ---"
for i in 1 2 3; do
  curl -s -X POST "${BASE_URL}/orders" \
    -H "Content-Type: application/json" \
    -d "{\"customer\": \"Customer ${i}\", \"items\": [\"item-a\", \"item-b\"], \"total\": $((i * 25)).99}" \
    | python -m json.tool
done

# List orders
echo -e "\n--- Listing Orders ---"
ORDERS=$(curl -s "${BASE_URL}/orders")
echo "${ORDERS}" | python -m json.tool

# Get first order ID
ORDER_ID=$(echo "${ORDERS}" | python -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# Update status
echo -e "\n--- Updating Order ${ORDER_ID} to processing ---"
curl -s -X PATCH "${BASE_URL}/orders/${ORDER_ID}/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "processing"}' \
  | python -m json.tool

echo -e "\n--- Updating Order ${ORDER_ID} to completed ---"
curl -s -X PATCH "${BASE_URL}/orders/${ORDER_ID}/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}' \
  | python -m json.tool

# Cancel last order
LAST_ID=$(echo "${ORDERS}" | python -c "import sys,json; print(json.load(sys.stdin)[-1]['id'])")
echo -e "\n--- Cancelling Order ${LAST_ID} ---"
curl -s -X DELETE "${BASE_URL}/orders/${LAST_ID}" | python -m json.tool

# Final state
echo -e "\n--- Final State ---"
curl -s "${BASE_URL}/orders" | python -m json.tool

# Metrics
echo -e "\n--- Metrics (first 20 lines) ---"
curl -s "${BASE_URL}/metrics" | head -20

echo -e "\n==> Done!"
