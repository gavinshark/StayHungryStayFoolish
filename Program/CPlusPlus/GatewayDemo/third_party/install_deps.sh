#!/bin/bash
# 自动安装第三方依赖脚本

set -e  # 遇到错误立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "安装第三方依赖库"
echo "=========================================="

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}错误: 未找到git命令，请先安装git${NC}"
    exit 1
fi

# 安装Asio
echo -e "\n${YELLOW}[1/4] 安装 Asio (standalone)...${NC}"
if [ -d "asio" ]; then
    echo "Asio已存在，跳过..."
else
    git clone https://github.com/chriskohlhoff/asio.git
    cd asio
    git checkout asio-1-28-0 || git checkout master
    cd ..
    echo -e "${GREEN}✓ Asio安装完成${NC}"
fi

# 安装nlohmann/json
echo -e "\n${YELLOW}[2/4] 安装 nlohmann/json...${NC}"
if [ -d "json" ]; then
    echo "nlohmann/json已存在，跳过..."
else
    git clone https://github.com/nlohmann/json.git
    cd json
    git checkout v3.11.3 || git checkout master
    cd ..
    echo -e "${GREEN}✓ nlohmann/json安装完成${NC}"
fi

# 安装spdlog
echo -e "\n${YELLOW}[3/4] 安装 spdlog...${NC}"
if [ -d "spdlog" ]; then
    echo "spdlog已存在，跳过..."
else
    git clone https://github.com/gabime/spdlog.git
    cd spdlog
    git checkout v1.12.0 || git checkout master
    cd ..
    echo -e "${GREEN}✓ spdlog安装完成${NC}"
fi

# 安装http-parser (可选)
echo -e "\n${YELLOW}[4/4] 安装 http-parser (可选)...${NC}"
read -p "是否安装http-parser? (y/n) [默认: n]: " install_http_parser
install_http_parser=${install_http_parser:-n}

if [[ "$install_http_parser" =~ ^[Yy]$ ]]; then
    if [ -d "http-parser" ]; then
        echo "http-parser已存在，跳过..."
    else
        git clone https://github.com/nodejs/http-parser.git
        cd http-parser
        git checkout v2.9.4 || git checkout master
        cd ..
        echo -e "${GREEN}✓ http-parser安装完成${NC}"
    fi
else
    echo "跳过http-parser安装"
fi

# 验证安装
echo -e "\n${YELLOW}验证安装...${NC}"
all_ok=true

if [ -f "asio/asio/include/asio.hpp" ]; then
    echo -e "${GREEN}✓ Asio: OK${NC}"
else
    echo -e "${RED}✗ Asio: 未找到${NC}"
    all_ok=false
fi

if [ -f "json/include/nlohmann/json.hpp" ]; then
    echo -e "${GREEN}✓ nlohmann/json: OK${NC}"
else
    echo -e "${RED}✗ nlohmann/json: 未找到${NC}"
    all_ok=false
fi

if [ -f "spdlog/include/spdlog/spdlog.h" ]; then
    echo -e "${GREEN}✓ spdlog: OK${NC}"
else
    echo -e "${RED}✗ spdlog: 未找到${NC}"
    all_ok=false
fi

if [ -f "http-parser/http_parser.h" ]; then
    echo -e "${GREEN}✓ http-parser: OK${NC}"
fi

echo ""
echo "=========================================="
if [ "$all_ok" = true ]; then
    echo -e "${GREEN}所有依赖安装成功！${NC}"
    echo ""
    echo "下一步："
    echo "  cd ../build"
    echo "  cmake .."
    echo "  make"
else
    echo -e "${RED}部分依赖安装失败，请检查错误信息${NC}"
    exit 1
fi
echo "=========================================="
