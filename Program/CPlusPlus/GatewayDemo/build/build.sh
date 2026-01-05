#!/bin/bash
# CMake 构建脚本 - Linux/macOS

set -e

echo "=== C++ Gateway CMake Build Script ==="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR"
OUTPUT_DIR="$(dirname "$SCRIPT_DIR")/output"

# 清理旧的 CMake 缓存（可选）
if [ "$1" == "clean" ]; then
    echo "Cleaning CMake cache and build files..."
    rm -rf "$BUILD_DIR/CMakeCache.txt"
    rm -rf "$BUILD_DIR/CMakeFiles"
    rm -rf "$BUILD_DIR/cmake_install.cmake"
    rm -rf "$BUILD_DIR/Makefile"
    rm -rf "$OUTPUT_DIR"
    echo "Clean complete."
    exit 0
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/obj"

# 进入构建目录
cd "$BUILD_DIR"

# 运行 CMake 配置
echo "Running CMake configuration..."
cmake -DCMAKE_BUILD_TYPE=Release .

echo ""
echo "Building project..."
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

echo ""
echo "=== Build Complete ==="
echo "Executable: $OUTPUT_DIR/gateway"
echo ""
echo "To run the gateway:"
echo "  ./output/gateway config/config.json"
echo ""
