#!/bin/bash

# HTTP Parser 单元测试编译和运行脚本

echo "=== Compiling HTTP Parser Unit Tests ==="

# 编译测试
g++ -std=c++17 -Wall -Wextra -I../include \
    test_http_parser.cpp \
    ../src/http_parser.cpp \
    -o test_http_parser

if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

echo "Compilation successful!"
echo ""

# 运行测试
echo "=== Running Tests ==="
./test_http_parser

# 保存退出码
exit_code=$?

# 清理
rm -f test_http_parser

exit $exit_code
