#!/bin/bash
# 测试日志功能

echo "=== 测试日志功能 ==="
echo ""

# 清理旧的日志
echo "1. 清理旧日志..."
rm -rf log/
echo "   ✅ 已删除 log 目录"
echo ""

# 启动测试后端
echo "2. 启动测试后端..."
python3 tests/test_backend.py 9001 > /dev/null 2>&1 &
BACKEND_PID=$!
echo "   ✅ 后端已启动 (PID: $BACKEND_PID)"
sleep 1
echo ""

# 启动网关
echo "3. 启动网关..."
./output/gateway config/config.json > /dev/null 2>&1 &
GATEWAY_PID=$!
echo "   ✅ 网关已启动 (PID: $GATEWAY_PID)"
sleep 2
echo ""

# 检查 log 目录
echo "4. 检查 log 目录..."
if [ -d "log" ]; then
    echo "   ✅ log 目录已自动创建"
    ls -lh log/
else
    echo "   ❌ log 目录未创建"
fi
echo ""

# 检查日志文件
echo "5. 检查日志文件..."
if [ -f "log/gateway.log" ]; then
    echo "   ✅ 日志文件已创建"
    echo ""
    echo "   日志内容："
    echo "   ----------------------------------------"
    cat log/gateway.log | head -20
    echo "   ----------------------------------------"
else
    echo "   ❌ 日志文件未创建"
fi
echo ""

# 发送测试请求
echo "6. 发送测试请求..."
curl -s http://localhost:8080/api/users > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 请求成功"
else
    echo "   ⚠️  请求失败（可能网关未完全启动）"
fi
sleep 1
echo ""

# 再次查看日志
echo "7. 查看更新后的日志..."
if [ -f "log/gateway.log" ]; then
    echo "   日志内容："
    echo "   ----------------------------------------"
    cat log/gateway.log
    echo "   ----------------------------------------"
    echo ""
    echo "   日志行数: $(wc -l < log/gateway.log)"
fi
echo ""

# 清理
echo "8. 清理进程..."
kill $GATEWAY_PID 2>/dev/null
kill $BACKEND_PID 2>/dev/null
sleep 1
echo "   ✅ 进程已停止"
echo ""

echo "=== 测试完成 ==="
echo ""
echo "日志文件位置: log/gateway.log"
echo "查看日志: cat log/gateway.log"
echo "实时查看: tail -f log/gateway.log"
