#!/bin/bash
# 编译并运行迁移测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "编译技术栈迁移测试"
echo "=========================================="

cd "$PROJECT_ROOT"

# 检查第三方库是否安装
if [ ! -d "third_party/spdlog" ] || [ ! -d "third_party/json" ]; then
    echo "错误: 第三方库未安装"
    echo "请先运行: ./third_party/install_deps.sh"
    exit 1
fi

# 编译测试
echo "编译测试程序..."
g++ -std=c++17 \
    -I third_party/spdlog/include \
    -I third_party/json/include \
    -o output/test_migration \
    tests/test_migration.cpp \
    -pthread

if [ $? -eq 0 ]; then
    echo "✅ 编译成功"
    echo ""
    echo "运行测试..."
    echo ""
    ./output/test_migration
else
    echo "❌ 编译失败"
    exit 1
fi
