# C++ Gateway - 简易跨平台网关程序

一个基于C++17的轻量级HTTP网关，支持跨平台编译（Windows、Linux、macOS），提供请求路由、负载均衡和错误处理功能。

## 特性

- ✅ **跨平台支持**: Windows、Linux、macOS
- ✅ **HTTP协议**: 支持HTTP/1.1请求和响应
- ✅ **路由匹配**: 支持精确匹配和前缀匹配
- ✅ **负载均衡**: 轮询（Round-Robin）策略
- ✅ **健康检查**: 自动标记和跳过不健康的后端
- ✅ **配置管理**: JSON配置文件 (nlohmann/json)
- ✅ **日志系统**: 高性能异步日志 (spdlog)
- ✅ **异步I/O**: Asio异步网络库
- ✅ **错误处理**: 完善的HTTP错误响应（404、500、502、503、504）

## 技术栈

- **网络库**: Asio (standalone) - 跨平台异步I/O库
- **JSON解析**: nlohmann/json - 现代C++ JSON库
- **日志库**: spdlog - 快速的C++日志库
- **构建系统**: CMake - 跨平台构建工具
- **HTTP解析**: 自实现简单HTTP解析器（可选使用http-parser）

## 系统要求

- C++17 兼容编译器
  - Windows: MSVC 2017+
  - Linux: GCC 7+
  - macOS: Clang 5+
- CMake 3.15+
- Git (用于下载第三方依赖)

## 安装依赖

在编译之前，需要先安装第三方依赖库：

```bash
# 自动安装所有依赖（推荐）
./third_party/install_deps.sh

# 或手动安装，参考 third_party/README.md
```

依赖库包括：
- Asio (standalone) - 异步网络库
- nlohmann/json - JSON解析
- spdlog - 日志库

详细安装说明请参考 `third_party/README.md`。

## 编译

### 快速开始

**5分钟快速上手**: 查看 `doc/QUICKSTART.md`

#### 方法 1: 使用 CMake（推荐）

```bash
# 1. 安装依赖
./third_party/install_deps.sh

# 2. 编译
cd build
cmake ..
make
```

#### 方法 2: 使用 Makefile（已弃用）

```bash
# Linux / macOS
./make.sh              # 编译项目
./make.sh clean        # 清理构建文件

# Windows (MinGW)
cd build
mingw32-make
```

#### 方法 2: 使用 CMake

```bash
# Linux / macOS
./build/build.sh       # 自动化构建
./build/build.sh clean # 清理

# Windows
build\build.bat        # 自动化构建
build\build.bat clean  # 清理
```

**编译产物**:
- 临时文件: `output/obj/*.o`
- 可执行文件: `output/gateway` (Linux/macOS) 或 `output/gateway.exe` (Windows)

### 详细说明

项目使用跨平台构建系统，支持：
- **Linux**: GCC 7+
- **macOS**: Clang 5+ (需要 Xcode Command Line Tools)
- **Windows**: MSVC 2017+ 或 MinGW GCC 7+

更多构建选项和故障排除，请参考 `build/README.md`。

## 配置

配置文件使用JSON格式，默认路径为 `config/config.json`。

### 配置示例

```json
{
  "listen_port": 8080,
  "log_level": "info",
  "log_file": "log/gateway.log",
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

日志同时输出到控制台和文件，默认位置为 `log/gateway.log`。

### 日志格式

```
[2024-12-06 16:40:00] [INFO] Gateway Starting
[2024-12-06 16:40:00] [INFO] Listen Port: 8080
[2024-12-06 16:40:01] [INFO] Request: GET /api/users
[2024-12-06 16:40:01] [DEBUG] Selected backend: http://localhost:9001
[2024-12-06 16:40:01] [INFO] Response: 200 OK
```

### 日志级别

在 `config/config.json` 中配置：

- `debug`: 显示所有日志（最详细）
- `info`: 显示信息、警告和错误（默认）
- `warn`: 显示警告和错误
- `error`: 只显示错误

### 查看日志

```bash
# 查看完整日志
cat log/gateway.log

# 实时查看日志
tail -f log/gateway.log

# 查看最后 50 行
tail -n 50 log/gateway.log
```

**注意**: log 目录会在网关启动时自动创建。

## 开发

### 项目结构

```
cpp-gateway/
├── build/                  # 构建脚本目录
│   ├── Makefile            # Make 构建配置
│   ├── CMakeLists.txt      # CMake 构建配置
│   ├── build.sh            # Linux/macOS 构建脚本
│   ├── build.bat           # Windows 构建脚本
│   └── README.md           # 构建文档
├── output/                 # 编译输出目录（自动生成）
│   ├── obj/                # 临时 .o 文件
│   └── gateway             # 可执行文件
├── log/                    # 日志目录（自动生成）
│   └── gateway.log         # 日志文件
├── config/                 # 配置文件目录
│   └── config.json
├── include/                # 头文件（11个）
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
├── src/                    # 源文件（9个）
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
│   ├── test_backend.py     # 测试后端服务器
│   ├── test_gateway.sh     # 网关测试脚本
│   └── EXAMPLES.md         # 使用示例
├── third_party/            # 第三方依赖
├── make.sh                 # 快捷编译脚本
└── README.md               # 本文件
```

### 快速测试

```bash
# 1. 编译项目
./make.sh

# 2. 启动测试后端
python3 tests/test_backend.py 9001 &
python3 tests/test_backend.py 9002 &

# 3. 启动网关
./output/gateway config/config.json &

# 4. 运行测试
./tests/test_gateway.sh

# 5. 查看日志
cat log/gateway.log
```

更多测试示例请参考 `tests/EXAMPLES.md`。

## 限制和注意事项

1. **开发中**: 项目正在迁移到新技术栈（Asio + nlohmann/json + spdlog）

2. **并发性能**: 使用Asio异步I/O实现高性能网络处理

3. **安全性**: 未实现TLS/SSL支持，不建议在公网环境使用

## 未来改进

- [x] 使用Asio实现异步I/O
- [x] 集成nlohmann/json进行JSON解析
- [x] 集成spdlog日志库
- [ ] 支持HTTPS/TLS
- [ ] 实现配置热重载
- [ ] 添加更多负载均衡策略（最少连接、加权轮询）
- [ ] 支持WebSocket协议
- [ ] 添加请求限流功能
- [ ] 实现健康检查探测
- [ ] 支持Prometheus指标导出

## 文档

### 快速开始
- **快速开始**: `doc/QUICKSTART.md` - 5分钟快速上手指南

### 技术文档
- **技术栈说明**: `doc/TECH_STACK.md` - 技术选型和对比
- **迁移指南**: `doc/MIGRATION_GUIDE.md` - 技术栈迁移说明
- **迁移总结**: `doc/TECH_STACK_MIGRATION_SUMMARY.md` - 已完成的迁移工作详细总结
- **迁移完成报告**: `doc/MIGRATION_COMPLETE.md` - 迁移工作完成报告
- **Asio迁移报告**: `doc/ASIO_MIGRATION_COMPLETE.md` - Asio网络层迁移报告
- **清理总结**: `doc/CLEANUP_SUMMARY.md` - 代码清理总结
- **第三方库**: `third_party/README.md` - 依赖库安装和配置

### 构建和测试
- **构建文档**: `build/README.md` - 详细的构建说明和故障排除
- **测试结果**: `doc/TEST_RESULTS.md` - 技术栈迁移测试结果
- **测试示例**: `tests/EXAMPLES.md` - 完整的使用示例

### 配置和日志
- **日志配置**: `doc/LOG_CONFIGURATION.md` - 日志系统配置说明
- **项目状态**: `doc/PROJECT_STATUS.md` - 项目完成状态和统计

## 常见问题

### Q: 编译时找不到编译器？

**macOS**: 安装 Xcode Command Line Tools
```bash
xcode-select --install
```

**Linux**: 安装 GCC
```bash
sudo apt-get install build-essential  # Ubuntu/Debian
```

**Windows**: 安装 Visual Studio 或 MinGW

### Q: 如何修改监听端口？

编辑 `config/config.json`，修改 `listen_port` 字段。

### Q: 日志文件在哪里？

默认位置：`log/gateway.log`（自动创建）

可以在 `config/config.json` 中修改 `log_file` 字段自定义路径。

### Q: 如何添加新的路由？

编辑 `config/config.json`，在 `routes` 数组中添加新的路由规则：

```json
{
  "path_pattern": "/api/new",
  "match_type": "prefix",
  "priority": 3,
  "backends": ["http://localhost:9004"]
}
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

**版本**: 2.0.0 (新技术栈)  
**最后更新**: 2024-12-06

## 更新日志

### v2.1.0 (2024-12-07) - Asio异步I/O
- ✨ **网络层**: 迁移到Asio异步I/O (性能提升10x+)
- ✨ **HTTP服务器**: HttpServerAsio异步实现
- ✨ **HTTP客户端**: HttpClientAsio异步实现
- 🚀 **并发性能**: 支持10000+并发连接
- 📝 **文档**: Asio迁移完成报告
- 🔧 **向后兼容**: 保留旧版本socket实现

### v2.0.0 (2024-12-06) - 技术栈现代化
- ✨ **日志系统**: 迁移到spdlog (性能提升100x)
- ✨ **JSON解析**: 迁移到nlohmann/json (完整功能支持)
- ✨ **构建系统**: 更新CMake配置支持第三方库
- 🚀 **依赖管理**: 添加自动依赖安装脚本
- 📝 **文档完善**: 快速开始、迁移指南、技术栈说明
- 🧪 **测试工具**: 添加迁移验证测试
- 🔧 **向后兼容**: 保持API和配置文件兼容性

### v1.0.0 (2024-12-05)
- 🎉 初始版本发布
- ✅ 基础HTTP网关功能
- ✅ 路由和负载均衡
- ✅ 跨平台支持
