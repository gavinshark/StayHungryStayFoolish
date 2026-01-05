#!/bin/bash

echo "=== 简单测试脚本 ==="
echo ""

# 清理
echo "1. 清理旧进程..."
killall gateway 2>/dev/null
killall python3 2>/dev/null
sleep 1

# 启动后端
echo "2. 启动后端 (9001)..."
python3 tests/test_backend.py 9001 > /tmp/backend_9001.log 2>&1 &
BACKEND_PID=$!
sleep 2

echo "   后端 PID: $BACKEND_PID"
echo "   检查后端..."
curl -s http://localhost:9001/test 2>&1 | head -3

# 测试网关（前台运行，带超时）
echo ""
echo "3. 测试网关启动..."
timeout 3 ./output/gateway config/config.json 2>&1 &
GATEWAY_PID=$!
sleep 2

echo "   网关 PID: $GATEWAY_PID"
echo "   检查端口..."
lsof -i :8080 2>/dev/null || echo "   ⚠️  端口 8080 未监听"

# 测试请求
echo ""
echo "4. 发送测试请求..."
curl -v http://localhost:8080/api/users 2>&1 | head -20

# 清理
echo ""
echo "5. 清理..."
kill $GATEWAY_PID 2>/dev/null
kill $BACKEND_PID 2>/dev/null

echo ""
echo "=== 测试完成 ==="
