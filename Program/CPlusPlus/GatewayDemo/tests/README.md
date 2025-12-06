# 测试目录

本目录包含项目的所有测试文件和测试脚本。

## 📁 文件列表

### 测试脚本

| 文件 | 说明 | 用途 |
|------|------|------|
| `test_gateway.sh` | 网关功能测试 | 测试路由、负载均衡、错误处理 |
| `test_simple.sh` | 简单测试脚本 | 快速测试网关基本功能 |
| `test_log.sh` | 日志功能测试 | 测试日志系统 |

### 测试后端

| 文件 | 说明 |
|------|------|
| `test_backend.py` | Python 测试后端服务器 |

### 文档

| 文件 | 说明 |
|------|------|
| `EXAMPLES.md` | 详细的使用示例 |
| `README.md` | 本文件 |

## 🚀 快速开始

### 1. 完整测试

```bash
# 运行完整的网关测试
./tests/test_gateway.sh
```

### 2. 简单测试

```bash
# 快速测试基本功能
./tests/test_simple.sh
```

### 3. 日志测试

```bash
# 测试日志功能
./tests/test_log.sh
```

## 📝 测试步骤

### 手动测试

```bash
# 1. 编译项目
./make.sh

# 2. 启动测试后端
python3 tests/test_backend.py 9001 &
python3 tests/test_backend.py 9002 &

# 3. 启动网关
./output/gateway config/config.json &

# 4. 发送测试请求
curl http://localhost:8080/api/users
curl http://localhost:8080/health

# 5. 查看日志
cat log/gateway.log

# 6. 清理
killall gateway python3
```

## 🧪 测试场景

### 1. 路由测试

```bash
# 精确匹配
curl http://localhost:8080/health

# 前缀匹配
curl http://localhost:8080/api/users
curl http://localhost:8080/api/orders

# 404 测试
curl http://localhost:8080/nonexistent
```

### 2. 负载均衡测试

```bash
# 启动多个后端
python3 tests/test_backend.py 9001 &
python3 tests/test_backend.py 9002 &

# 发送多个请求，观察轮询
for i in {1..6}; do
  curl -s http://localhost:8080/api/users | grep port
done
```

### 3. 错误处理测试

```bash
# 后端不可用 (503)
# 不启动后端，直接请求
curl -i http://localhost:8080/api/users

# 路由未找到 (404)
curl -i http://localhost:8080/nonexistent
```

### 4. POST 请求测试

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123, "item": "test"}'
```

## 📊 测试后端说明

### test_backend.py

简单的 HTTP 服务器，用于模拟后端服务。

**启动**:
```bash
python3 tests/test_backend.py <port>
```

**响应格式**:
```json
{
  "message": "Hello from test backend",
  "path": "/api/users",
  "method": "GET",
  "port": 9001
}
```

**特点**:
- 支持 GET 和 POST 请求
- 返回 JSON 格式响应
- 显示请求路径和方法
- 显示后端端口（用于验证负载均衡）

## 🔍 调试技巧

### 查看实时日志

```bash
tail -f log/gateway.log
```

### 查看详细请求

```bash
curl -v http://localhost:8080/api/users
```

### 检查端口占用

```bash
lsof -i :8080  # 网关
lsof -i :9001  # 后端1
lsof -i :9002  # 后端2
```

### 查看进程

```bash
ps aux | grep gateway
ps aux | grep test_backend
```

## 📋 测试检查清单

运行测试前确保：

- [ ] 项目已编译 (`./make.sh`)
- [ ] 配置文件正确 (`config/config.json`)
- [ ] 端口未被占用 (8080, 9001, 9002)
- [ ] Python 3 已安装
- [ ] curl 已安装

## 🎯 预期结果

### 成功的测试

```bash
# 1. 网关启动
Gateway is running. Press Ctrl+C to stop.

# 2. 请求成功
HTTP/1.1 200 OK
Content-Type: application/json
{"message": "Hello from test backend", ...}

# 3. 日志正常
[2024-12-06 21:14:24] [INFO] Request: GET /api/users
[2024-12-06 21:14:24] [INFO] Response: 200 OK
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Connection refused | 网关未启动 | 检查网关进程 |
| 404 Not Found | 路由未配置 | 检查 config.json |
| 503 Service Unavailable | 后端未启动 | 启动测试后端 |
| 端口已占用 | 端口冲突 | 修改配置或停止占用进程 |

## 📚 相关文档

- `EXAMPLES.md` - 详细的使用示例
- `../README.md` - 项目主文档
- `../doc/GATEWAY_FLOW.md` - 网关请求流程
- `../doc/HTTP_CLIENT_IMPLEMENTATION.md` - HTTP 客户端实现

## 🎉 测试组织标准

### 规则

1. **所有测试文件都放在 tests/ 目录**
2. **测试脚本使用 test_*.sh 命名**
3. **测试后端使用 test_*.py 命名**
4. **测试文档使用大写 .md 文件**

### 添加新测试

```bash
# 1. 创建测试脚本
vim tests/test_new_feature.sh

# 2. 添加执行权限
chmod +x tests/test_new_feature.sh

# 3. 更新 README.md
vim tests/README.md

# 4. 运行测试
./tests/test_new_feature.sh
```

---

**最后更新**: 2024-12-06  
**测试脚本数量**: 3  
**状态**: ✅ 所有测试文件已组织
