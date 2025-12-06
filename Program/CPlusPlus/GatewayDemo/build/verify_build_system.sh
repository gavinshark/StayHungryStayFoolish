#!/bin/bash
# 验证构建系统配置

echo "=== 构建系统验证 ==="
echo ""

# 检查必要的文件
echo "检查构建文件..."
files=(
    "Makefile"
    "CMakeLists.txt"
    "build.sh"
    "build.bat"
    "README.md"
)

all_ok=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
        all_ok=false
    fi
done

echo ""
echo "检查源文件..."
src_files=(
    "../src/main.cpp"
    "../src/gateway.cpp"
    "../src/http_server.cpp"
    "../src/http_client.cpp"
    "../src/http_parser.cpp"
    "../src/config_manager.cpp"
    "../src/logger.cpp"
    "../src/request_router.cpp"
    "../src/load_balancer.cpp"
)

for file in "${src_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $(basename $file)"
    else
        echo "  ❌ $(basename $file) (缺失)"
        all_ok=false
    fi
done

echo ""
echo "检查头文件..."
inc_files=(
    "../include/gateway.hpp"
    "../include/http_server.hpp"
    "../include/http_client.hpp"
    "../include/http_parser.hpp"
    "../include/config_manager.hpp"
    "../include/logger.hpp"
    "../include/request_router.hpp"
    "../include/load_balancer.hpp"
    "../include/types.hpp"
    "../include/http_types.hpp"
    "../include/config_types.hpp"
)

for file in "${inc_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $(basename $file)"
    else
        echo "  ❌ $(basename $file) (缺失)"
        all_ok=false
    fi
done

echo ""
echo "检查脚本权限..."
if [ -x "build.sh" ]; then
    echo "  ✅ build.sh 可执行"
else
    echo "  ⚠️  build.sh 不可执行 (运行: chmod +x build.sh)"
fi

if [ -x "../make.sh" ]; then
    echo "  ✅ make.sh 可执行"
else
    echo "  ⚠️  make.sh 不可执行 (运行: chmod +x make.sh)"
fi

echo ""
echo "检查编译器..."
if command -v g++ &> /dev/null; then
    echo "  ✅ g++ 已安装: $(g++ --version | head -n 1)"
elif command -v clang++ &> /dev/null; then
    echo "  ✅ clang++ 已安装: $(clang++ --version | head -n 1)"
else
    echo "  ❌ 未找到 C++ 编译器"
    all_ok=false
fi

if command -v make &> /dev/null; then
    echo "  ✅ make 已安装: $(make --version | head -n 1)"
else
    echo "  ⚠️  make 未安装"
fi

if command -v cmake &> /dev/null; then
    echo "  ✅ cmake 已安装: $(cmake --version | head -n 1)"
else
    echo "  ⚠️  cmake 未安装"
fi

echo ""
if [ "$all_ok" = true ]; then
    echo "✅ 构建系统验证通过！"
    echo ""
    echo "可以开始编译："
    echo "  cd .."
    echo "  ./make.sh"
    exit 0
else
    echo "❌ 构建系统验证失败，请检查缺失的文件"
    exit 1
fi
