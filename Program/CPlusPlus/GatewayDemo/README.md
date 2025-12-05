# C++ Gateway - 简易跨平台网关程序

一个基于C++17的轻量级HTTP网关，支持跨平台编译（Windows、Linux、macOS），提供请求路由、负载均衡和错误处理功能。

## 特性

- ✅ **跨平台支持**: Windows、Linux、macOS
- ✅ **HTTP协议**: 支持HTTP/1.1请求和响应
- ✅ **路由匹配**: 支持精确匹配和前缀匹配
- ✅ **负载均衡**: 轮询（Round-Robin）策略
- ✅ **健康检查**: 自动标记和跳过不健康的后端
- ✅ **配置管理**: JSON配置文件
- ✅ **日志系统**: 多级别日志，同时输出到控制台和文件
- ✅ **错误处理**: 完善的HTTP错误响应（404、500、502、503、504）

## 系统要求

- C++17 兼容编译器
  - Windows: MSVC 2017+
  - Linux: GCC 7+
  - macOS: Clang 5+
- CMake 3.15+

## 编译

### 1. 克隆项目

```bash
git clone <repository-url>
cd cpp-gateway
```

### 2. 安装第三方依赖（可选）

如果需要完整功能，请参考 `third_party/README.md` 安装依赖库。

### 3. 编译项目

#### Linux / macOS

```bash
mkdir build
cd build
cmake ..
make
```

#### Windows

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

编译完成后，可执行文件位于 `output/gateway`。

## 配置

配置文件使用JSON格式，默认路径为 `config/config.json`。

### 配置示例

```json
{
  "listen_port": 8080,
  "log_level": "info",
  "log_file": "gateway.log",
  "backend_timeout_ms": 5000,
  "client_timeout_ms": 30000,
  "routes": [
    {
      "path_pattern": "/api/users",
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

### 配置项说明

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `listen_port` | 整数 | 网关监听端口 |
| `log_level` | 字符串 | 日志级别：debug, info, warn, error |
| `log_file` | 字符串 | 日志文件路径 |
| `backend_timeout_ms` | 整数 | 后端请求超时时间（毫秒） |
| `client_timeout_ms` | 整数 | 客户端连接超时时间（毫秒） |
| `routes` | 数组 | 路由规则列表 |

### 路由配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `path_pattern` | 字符串 | 路径模式，如 "/api/users" |
| `match_type` | 字符串 | 匹配类型：exact（精确）或 prefix（前缀） |
| `priority` | 整数 | 优先级，数值越小优先级越高 |
| `backends` | 数组 | 后端服务URL列表 |

## 运行

### 启动网关

```bash
# 使用默认配置
./output/gateway

# 指定配置文件
./output/gateway /path/to/config.json
```

### 测试网关

启动网关后，可以使用curl测试：

```bash
# 发送GET请求
curl http://localhost:8080/api/users

# 发送POST请求
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123}'
```

## 架构

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────┐
│          Gateway                    │
│  ┌──────────────────────────────┐  │
│  │   HTTP Server (Listener)     │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│  ┌────────────▼─────────────────┐  │
│  │   Request Router             │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│  ┌────────────▼─────────────────┐  │
│  │   Load Balancer              │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│  ┌────────────▼─────────────────┐  │
│  │   HTTP Client (Forwarder)    │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │ HTTP Request
       ▼
┌─────────────┐
│   Backend   │
│   Service   │
└─────────────┘
```

## 错误码

| HTTP状态码 | 说明 |
|-----------|------|
| 404 | 未找到匹配的路由 |
| 500 | 网关内部错误 |
| 502 | 后端连接失败 |
| 503 | 所有后端服务不可用 |
| 504 | 后端响应超时 |

## 日志

日志同时输出到控制台和文件，格式如下：

```
[2024-12-05 10:30:45] [INFO] Gateway Starting
[2024-12-05 10:30:45] [INFO] Listen Port: 8080
[2024-12-05 10:30:46] [INFO] Request: GET /api/users
[2024-12-05 10:30:46] [DEBUG] Selected backend: http://localhost:9001
[2024-12-05 10:30:46] [INFO] Response: 200 OK
```

## 开发

### 项目结构

```
cpp-gateway/
├── CMakeLists.txt          # CMake构建配置
├── README.md               # 项目文档
├── config/                 # 配置文件目录
│   └── config.json
├── include/                # 头文件
│   ├── types.hpp
│   ├── http_types.hpp
│   ├── config_types.hpp
│   ├── http_parser.hpp
│   ├── config_manager.hpp
│   ├── logger.hpp
│   ├── request_router.hpp
│   ├── load_balancer.hpp
│   ├── http_client.hpp
│   ├── http_server.hpp
│   └── gateway.hpp
├── src/                    # 源文件
│   ├── main.cpp
│   ├── http_parser.cpp
│   ├── config_manager.cpp
│   ├── logger.cpp
│   ├── request_router.cpp
│   ├── load_balancer.cpp
│   ├── http_client.cpp
│   ├── http_server.cpp
│   └── gateway.cpp
├── tests/                  # 测试文件
└── third_party/            # 第三方依赖
```

### 运行测试

```bash
cd build
make gateway_tests
./bin/gateway_tests
```

## 限制和注意事项

1. **简化实现**: 当前版本为演示实现，HTTP客户端和服务器使用了简化的同步I/O。生产环境建议使用Asio等异步I/O库。

2. **JSON解析**: 配置管理器使用了简化的JSON解析。建议使用nlohmann/json库进行完整的JSON解析。

3. **并发性能**: 当前实现为每个连接创建新线程。高并发场景建议使用线程池或异步I/O。

4. **安全性**: 未实现TLS/SSL支持，不建议在公网环境使用。

## 未来改进

- [ ] 使用Asio实现真正的异步I/O
- [ ] 集成nlohmann/json进行完整的JSON解析
- [ ] 支持HTTPS/TLS
- [ ] 实现配置热重载
- [ ] 添加更多负载均衡策略（最少连接、加权轮询）
- [ ] 支持WebSocket协议
- [ ] 添加请求限流功能
- [ ] 实现健康检查探测
- [ ] 支持Prometheus指标导出

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
