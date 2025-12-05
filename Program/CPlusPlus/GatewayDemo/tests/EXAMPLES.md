# 使用示例

本文档提供了C++ Gateway的各种使用示例。

## 基础示例

### 示例1: 简单的GET请求转发

**配置** (`config/config.json`):
```json
{
  "listen_port": 8080,
  "routes": [
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 1,
      "backends": ["http://localhost:9001"]
    }
  ]
}
```

**测试**:
```bash
# 启动后端
python3 test_backend.py 9001 &

# 启动网关
./gateway config/config.json &

# 发送请求
curl http://localhost:8080/api/users
```

**预期响应**:
```json
{
  "message": "Hello from test backend",
  "path": "/api/users",
  "method": "GET",
  "port": 9001
}
```

---

## 负载均衡示例

### 示例2: 轮询负载均衡

**配置**:
```json
{
  "listen_port": 8080,
  "routes": [
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 1,
      "backends": [
        "http://localhost:9001",
        "http://localhost:9002",
        "http://localhost:9003"
      ]
    }
  ]
}
```

**测试**:
```bash
# 启动3个后端
python3 test_backend.py 9001 &
python3 test_backend.py 9002 &
python3 test_backend.py 9003 &

# 启动网关
./gateway config/config.json &

# 发送多个请求，观察轮询
for i in {1..6}; do
  echo "Request $i:"
  curl -s http://localhost:8080/api/test | grep port
  sleep 0.5
done
```

**预期输出**:
```
Request 1: "port": 9001
Request 2: "port": 9002
Request 3: "port": 9003
Request 4: "port": 9001
Request 5: "port": 9002
Request 6: "port": 9003
```

---

## 路由匹配示例

### 示例3: 精确匹配 vs 前缀匹配

**配置**:
```json
{
  "listen_port": 8080,
  "routes": [
    {
      "path_pattern": "/health",
      "match_type": "exact",
      "priority": 1,
      "backends": ["http://localhost:9001"]
    },
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 2,
      "backends": ["http://localhost:9002"]
    }
  ]
}
```

**测试**:
```bash
# /health - 精确匹配，路由到9001
curl http://localhost:8080/health

# /health/check - 不匹配精确规则，返回404
curl http://localhost:8080/health/check

# /api/users - 前缀匹配，路由到9002
curl http://localhost:8080/api/users

# /api - 前缀匹配，路由到9002
curl http://localhost:8080/api
```

---

## 优先级示例

### 示例4: 路由优先级

**配置**:
```json
{
  "listen_port": 8080,
  "routes": [
    {
      "path_pattern": "/api/special",
      "match_type": "prefix",
      "priority": 1,
      "backends": ["http://localhost:9001"]
    },
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 2,
      "backends": ["http://localhost:9002"]
    }
  ]
}
```

**测试**:
```bash
# /api/special/users - 匹配优先级1，路由到9001
curl http://localhost:8080/api/special/users

# /api/users - 匹配优先级2，路由到9002
curl http://localhost:8080/api/users
```

**说明**: 优先级数值越小，优先级越高。

---

## 错误处理示例

### 示例5: 404 Not Found

**测试**:
```bash
# 请求不存在的路由
curl -i http://localhost:8080/nonexistent
```

**预期响应**:
```
HTTP/1.1 404 Not Found
Content-Type: text/plain
Content-Length: 9

Not Found
```

### 示例6: 503 Service Unavailable

**场景**: 所有后端都不可用

**测试**:
```bash
# 不启动任何后端，直接请求
./gateway config/config.json &
curl -i http://localhost:8080/api/users
```

**预期响应**:
```
HTTP/1.1 503 Service Unavailable
Content-Type: text/plain
Content-Length: 19

Service Unavailable
```

---

## POST请求示例

### 示例7: 转发POST请求

**测试**:
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 12345,
    "product": "Widget",
    "quantity": 10
  }'
```

**预期响应**:
```json
{
  "message": "POST received",
  "path": "/api/orders",
  "method": "POST",
  "body": "{\"order_id\": 12345, \"product\": \"Widget\", \"quantity\": 10}",
  "port": 9001
}
```

---

## 日志级别示例

### 示例8: 不同的日志级别

**DEBUG级别** (`config/config.json`):
```json
{
  "listen_port": 8080,
  "log_level": "debug",
  "log_file": "gateway.log"
}
```

**日志输出**:
```
[2024-12-05 10:30:45] [INFO] Gateway Starting
[2024-12-05 10:30:46] [INFO] Request: GET /api/users
[2024-12-05 10:30:46] [DEBUG] Selected backend: http://localhost:9001
[2024-12-05 10:30:46] [DEBUG] Sending request to localhost:9001/api/users
[2024-12-05 10:30:46] [INFO] Response: 200 OK
```

**INFO级别**:
```json
{
  "log_level": "info"
}
```

**日志输出**:
```
[2024-12-05 10:30:45] [INFO] Gateway Starting
[2024-12-05 10:30:46] [INFO] Request: GET /api/users
[2024-12-05 10:30:46] [INFO] Response: 200 OK
```

---

## 超时配置示例

### 示例9: 配置超时时间

**配置**:
```json
{
  "listen_port": 8080,
  "backend_timeout_ms": 3000,
  "client_timeout_ms": 30000,
  "routes": [...]
}
```

**说明**:
- `backend_timeout_ms`: 后端响应超时（3秒）
- `client_timeout_ms`: 客户端连接超时（30秒）

---

## 多路由配置示例

### 示例10: 复杂的路由配置

**配置**:
```json
{
  "listen_port": 8080,
  "log_level": "info",
  "log_file": "gateway.log",
  "backend_timeout_ms": 5000,
  "client_timeout_ms": 30000,
  "routes": [
    {
      "path_pattern": "/health",
      "match_type": "exact",
      "priority": 0,
      "backends": ["http://localhost:9001"]
    },
    {
      "path_pattern": "/api/v2",
      "match_type": "prefix",
      "priority": 1,
      "backends": [
        "http://localhost:9002",
        "http://localhost:9003"
      ]
    },
    {
      "path_pattern": "/api/v1",
      "match_type": "prefix",
      "priority": 2,
      "backends": ["http://localhost:9001"]
    },
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 3,
      "backends": [
        "http://localhost:9001",
        "http://localhost:9002",
        "http://localhost:9003"
      ]
    },
    {
      "path_pattern": "/static",
      "match_type": "prefix",
      "priority": 4,
      "backends": ["http://localhost:9004"]
    }
  ]
}
```

**路由规则**:
1. `/health` → 精确匹配 → 9001
2. `/api/v2/*` → 前缀匹配 → 9002, 9003（轮询）
3. `/api/v1/*` → 前缀匹配 → 9001
4. `/api/*` → 前缀匹配 → 9001, 9002, 9003（轮询）
5. `/static/*` → 前缀匹配 → 9004

---

## 性能测试示例

### 示例11: 使用Apache Bench测试

```bash
# 1000个请求，10个并发
ab -n 1000 -c 10 http://localhost:8080/api/users

# 查看结果
# Requests per second: XXX [#/sec]
# Time per request: XXX [ms]
```

### 示例12: 使用wrk测试

```bash
# 4个线程，100个连接，持续30秒
wrk -t4 -c100 -d30s http://localhost:8080/api/users

# 查看结果
# Requests/sec: XXXX
# Transfer/sec: XXX KB
```

---

## 故障转移示例

### 示例13: 后端故障自动切换

**场景**: 一个后端失败，自动切换到其他后端

**配置**:
```json
{
  "routes": [
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 1,
      "backends": [
        "http://localhost:9001",
        "http://localhost:9002"
      ]
    }
  ]
}
```

**测试**:
```bash
# 启动两个后端
python3 test_backend.py 9001 &
python3 test_backend.py 9002 &

# 启动网关
./gateway config/config.json &

# 发送请求（正常轮询）
curl http://localhost:8080/api/test  # → 9001
curl http://localhost:8080/api/test  # → 9002

# 停止9001
kill <9001的进程ID>

# 继续发送请求（自动切换到9002）
curl http://localhost:8080/api/test  # → 9002
curl http://localhost:8080/api/test  # → 9002
```

---

## 完整的端到端示例

### 示例14: 完整的微服务网关场景

**架构**:
```
Client → Gateway:8080 → User Service:9001
                      → Order Service:9002
                      → Product Service:9003
```

**配置**:
```json
{
  "listen_port": 8080,
  "log_level": "info",
  "routes": [
    {
      "path_pattern": "/api/users",
      "match_type": "prefix",
      "priority": 1,
      "backends": ["http://localhost:9001"]
    },
    {
      "path_pattern": "/api/orders",
      "match_type": "prefix",
      "priority": 2,
      "backends": ["http://localhost:9002"]
    },
    {
      "path_pattern": "/api/products",
      "match_type": "prefix",
      "priority": 3,
      "backends": ["http://localhost:9003"]
    }
  ]
}
```

**启动所有服务**:
```bash
# 启动后端服务
python3 tests/test_backend.py 9001 &  # User Service
python3 tests/test_backend.py 9002 &  # Order Service
python3 tests/test_backend.py 9003 &  # Product Service

# 启动网关
./output/gateway config/config.json &
```

**测试各个服务**:
```bash
# 用户服务
curl http://localhost:8080/api/users/123

# 订单服务
curl http://localhost:8080/api/orders/456

# 产品服务
curl http://localhost:8080/api/products/789
```

---

## 总结

这些示例展示了C++ Gateway的主要功能：
- ✅ 基础请求转发
- ✅ 负载均衡（轮询）
- ✅ 路由匹配（精确和前缀）
- ✅ 优先级处理
- ✅ 错误处理
- ✅ POST请求支持
- ✅ 日志级别控制
- ✅ 超时配置
- ✅ 故障转移

更多高级用法请参考 [README.md](README.md) 和 [QUICKSTART.md](QUICKSTART.md)。
