# 快速启动指南

本指南将帮助你快速编译和运行C++ Gateway。

## 前置要求

- C++17编译器（GCC 7+, Clang 5+, 或 MSVC 2017+）
- Make工具
- Python 3（用于测试后端，可选）

## 步骤1: 编译网关

### Linux / macOS

```bash
# 方式1: 使用快捷脚本（推荐）
./make.sh

# 方式2: 进入build目录编译
cd build && make

# 方式3: 使用CMake构建脚本
./build/build.sh
```

### Windows

```bash
# 使用构建脚本
build\build.bat

# 或手动编译
cd build
cmake ..
cmake --build . --config Release
```

编译成功后，会在 `output/` 目录生成 `gateway` 可执行文件。

## 步骤2: 启动测试后端（可选）

为了测试网关的转发功能，你可以启动一个或多个测试后端服务器：

```bash
# 终端1: 启动后端1（端口9001）
python3 test_backend.py 9001

# 终端2: 启动后端2（端口9002）
python3 test_backend.py 9002

# 终端3: 启动后端3（端口9003）
python3 test_backend.py 9003
```

## 步骤3: 启动网关

```bash
# 使用默认配置
./output/gateway

# 或指定配置文件
./output/gateway config/config.json
```

你应该看到类似的输出：

```
C++ Gateway v1.0.0
Loading configuration from: config/config.json
Gateway is running. Press Ctrl+C to stop.
```

## 步骤4: 测试网关

在新的终端窗口中运行测试：

```bash
# 使用测试脚本
./test_gateway.sh

# 或手动测试
curl http://localhost:8080/api/users
curl http://localhost:8080/api/orders
curl http://localhost:8080/health
```

## 预期结果

### 成功的请求

```bash
$ curl http://localhost:8080/api/users
{
  "message": "Hello from test backend",
  "path": "/api/users",
  "method": "GET",
  "port": 9001
}
```

### 404错误（路由未找到）

```bash
$ curl http://localhost:8080/nonexistent
Not Found
```

### 503错误（后端不可用）

如果没有启动后端服务器，你会看到：

```bash
$ curl http://localhost:8080/api/users
Service Unavailable
```

## 查看日志

网关会将日志输出到控制台和 `gateway.log` 文件：

```bash
# 实时查看日志
tail -f gateway.log

# 查看最近的日志
tail -n 50 gateway.log
```

日志示例：

```
[2024-12-05 10:30:45] [INFO] Gateway Starting
[2024-12-05 10:30:45] [INFO] Listen Port: 8080
[2024-12-05 10:30:46] [INFO] Request: GET /api/users
[2024-12-05 10:30:46] [DEBUG] Selected backend: http://localhost:9001
[2024-12-05 10:30:46] [INFO] Response: 200 OK
```

## 配置修改

编辑 `config/config.json` 来修改网关配置：

```json
{
  "listen_port": 8080,
  "log_level": "info",
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

修改后重启网关使配置生效。

## 停止服务

按 `Ctrl+C` 停止网关和后端服务器。

## 故障排查

### 编译错误

如果遇到编译错误，确保：
- C++编译器支持C++17标准
- 所有头文件路径正确

### 端口被占用

如果端口8080已被占用，修改 `config/config.json` 中的 `listen_port`。

### 连接被拒绝

确保后端服务器正在运行，并且URL配置正确。

## 下一步

- 阅读 [README.md](README.md) 了解更多功能
- 查看 [config/config.json](config/config.json) 了解配置选项
- 探索源代码了解实现细节

## 性能测试

使用 `ab` (Apache Bench) 或 `wrk` 进行性能测试：

```bash
# 使用ab测试
ab -n 1000 -c 10 http://localhost:8080/api/users

# 使用wrk测试
wrk -t4 -c100 -d30s http://localhost:8080/api/users
```

祝你使用愉快！
