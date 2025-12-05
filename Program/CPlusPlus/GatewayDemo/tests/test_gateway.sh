#!/bin/bash

# 测试网关功能的脚本

echo "=== Gateway Test Script ==="
echo ""

GATEWAY_URL="http://localhost:8080"

echo "1. Testing /api/users (should route to backend)"
curl -s "$GATEWAY_URL/api/users" | python3 -m json.tool 2>/dev/null || curl -s "$GATEWAY_URL/api/users"
echo ""
echo ""

echo "2. Testing /api/orders (should route to backend)"
curl -s "$GATEWAY_URL/api/orders" | python3 -m json.tool 2>/dev/null || curl -s "$GATEWAY_URL/api/orders"
echo ""
echo ""

echo "3. Testing /health (exact match)"
curl -s "$GATEWAY_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$GATEWAY_URL/health"
echo ""
echo ""

echo "4. Testing /nonexistent (should return 404)"
curl -s -w "\nHTTP Status: %{http_code}\n" "$GATEWAY_URL/nonexistent"
echo ""
echo ""

echo "5. Testing POST request"
curl -s -X POST "$GATEWAY_URL/api/orders" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123, "item": "test"}' | python3 -m json.tool 2>/dev/null || \
  curl -s -X POST "$GATEWAY_URL/api/orders" -H "Content-Type: application/json" -d '{"order_id": 123}'
echo ""
echo ""

echo "=== Test Complete ==="
