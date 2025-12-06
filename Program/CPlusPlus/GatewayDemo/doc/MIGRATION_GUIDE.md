# 技术栈迁移指南

本文档说明项目从简化实现迁移到现代C++技术栈的过程。

## 迁移状态

| 阶段 | 组件 | 状态 | 完成日期 |
|------|------|------|---------|
| 1 | 日志系统 (spdlog) | ✅ 完成 | 2024-12-06 |
| 2 | JSON解析 (nlohmann/json) | ✅ 完成 | 2024-12-06 |
| 3 | 网络层 (Asio) | ⏳ 待完成 | - |
| 4 | HTTP客户端 (Asio) | ⏳ 待完成 | - |
| 5 | HTTP解析器 | ⏳ 待完成 | - |

## 新技术栈

### 之前
- 自实现的简单socket封装
- 手写的简单JSON解析
- 基础的日志输出
- Makefile构建系统

### 现在
- **Asio (standalone)**: 跨平台异步I/O库
- **nlohmann/json**: 现代C++ JSON库
- **spdlog**: 快速的C++日志库
- **CMake**: 跨平台构建工具
- **http-parser**: 可选的HTTP解析器

## 迁移步骤

### 1. 安装依赖

```bash
# 自动安装所有依赖
./third_party/install_deps.sh

# 或查看手动安装说明
cat third_party/README.md
```

### 2. 更新CMake配置

CMakeLists.txt已更新以包含第三方库：

```cmake
# Asio
include_directories(${THIRD_PARTY_DIR}/asio/asio/include)
add_definitions(-DASIO_STANDALONE)

# nlohmann/json
include_directories(${THIRD_PARTY_DIR}/json/include)

# spdlog
include_directories(${THIRD_PARTY_DIR}/spdlog/include)
```

### 3. 代码迁移计划

#### 阶段1: 日志系统 (优先级: 高) ✅ 已完成
- [x] 将 `logger.cpp` 迁移到spdlog
- [x] 更新日志配置
- [x] 支持异步日志和rotating file
- [x] 保持向后兼容的API

**改进**:
- 使用spdlog的rotating_file_sink (10MB, 3个文件)
- 彩色控制台输出
- 格式化日志支持
- 更好的性能（异步写入）

#### 阶段2: JSON解析 (优先级: 高) ✅ 已完成
- [x] 将 `config_manager.cpp` 迁移到nlohmann/json
- [x] 简化配置解析代码
- [x] 完整的JSON解析支持
- [x] 更好的错误处理

**改进**:
- 使用nlohmann/json替代手写解析
- 支持默认值
- 更好的类型检查
- 清晰的错误信息

#### 阶段3: 网络层 (优先级: 中)
- [ ] 将 `http_server.cpp` 迁移到Asio
- [ ] 实现异步accept和read/write
- [ ] 使用io_context管理异步操作

#### 阶段4: HTTP客户端 (优先级: 中)
- [ ] 将 `http_client.cpp` 迁移到Asio
- [ ] 实现异步HTTP请求
- [ ] 支持连接池

#### 阶段5: HTTP解析器 (优先级: 低)
- [ ] 评估是否使用http-parser
- [ ] 或保持当前自实现的解析器

## 使用示例

### 使用spdlog

```cpp
#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/rotating_file_sink.h>

// 创建logger
auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
auto file_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
    "log/gateway.log", 1024 * 1024 * 10, 3);

std::vector<spdlog::sink_ptr> sinks{console_sink, file_sink};
auto logger = std::make_shared<spdlog::logger>("gateway", sinks.begin(), sinks.end());
spdlog::set_default_logger(logger);

// 使用
spdlog::info("Gateway starting on port {}", 8080);
spdlog::error("Failed to connect: {}", error_msg);
```

### 使用nlohmann/json

```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

// 解析JSON
std::ifstream file("config.json");
json config = json::parse(file);

// 访问字段
int port = config["listen_port"];
std::string log_level = config["log_level"];

// 遍历数组
for (auto& route : config["routes"]) {
    std::string path = route["path_pattern"];
    auto backends = route["backends"].get<std::vector<std::string>>();
}
```

### 使用Asio

```cpp
#include <asio.hpp>

// 创建io_context
asio::io_context io_context;

// 创建acceptor
asio::ip::tcp::acceptor acceptor(
    io_context, 
    asio::ip::tcp::endpoint(asio::ip::tcp::v4(), 8080)
);

// 异步accept
acceptor.async_accept([](std::error_code ec, asio::ip::tcp::socket socket) {
    if (!ec) {
        // 处理连接
        handle_connection(std::move(socket));
    }
});

// 运行事件循环
io_context.run();
```

## 兼容性说明

### 保持向后兼容
- 配置文件格式不变
- API接口保持一致
- 命令行参数不变

### 性能提升
- 异步I/O提升并发性能
- spdlog提供更快的日志输出
- nlohmann/json提供更好的JSON解析性能

## 构建说明

### 使用CMake（推荐）

```bash
cd build
cmake ..
make
```

### 使用旧的Makefile（已弃用）

旧的Makefile仍然可用，但不包含新的依赖库：

```bash
./make.sh
```

**注意**: 建议迁移到CMake构建系统。

## 测试

迁移后需要重新测试所有功能：

```bash
# 编译
cd build && cmake .. && make

# 运行单元测试
cd ../tests
./run_unit_tests.sh

# 运行集成测试
./test_gateway.sh
```

## 故障排除

### 问题: 找不到Asio头文件

```
fatal error: asio.hpp: No such file or directory
```

**解决方案**: 运行依赖安装脚本
```bash
./third_party/install_deps.sh
```

### 问题: CMake警告找不到库

```
CMake Warning: Asio not found at /path/to/third_party/asio/asio/include
```

**解决方案**: 检查目录结构，确保路径正确
```bash
ls third_party/asio/asio/include/asio.hpp
```

### 问题: 链接错误

**Windows**:
```cmake
target_link_libraries(gateway PRIVATE ws2_32 wsock32)
```

**Linux/macOS**:
```cmake
find_package(Threads REQUIRED)
target_link_libraries(gateway PRIVATE Threads::Threads)
```

## 参考资源

- [Asio教程](https://think-async.com/Asio/asio-1.28.0/doc/)
- [nlohmann/json文档](https://json.nlohmann.me/)
- [spdlog Wiki](https://github.com/gabime/spdlog/wiki)
- [CMake教程](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)

## 验证迁移

### 快速测试

运行迁移测试程序验证spdlog和nlohmann/json是否正确集成：

```bash
# 编译并运行测试
./tests/compile_migration_test.sh
```

测试内容：
- ✅ spdlog日志功能
- ✅ nlohmann/json解析和序列化
- ✅ 配置文件解析
- ⏭️ Asio (待完成)

### 完整测试

```bash
# 1. 编译项目
cd build && cmake .. && make && cd ..

# 2. 运行网关
./output/gateway config/config.json

# 3. 检查日志（应该看到spdlog格式的输出）
tail -f log/gateway.log
```

## 下一步

1. 查看快速开始: `doc/QUICKSTART.md`
2. 安装依赖: `./third_party/install_deps.sh`
3. 运行迁移测试: `./tests/compile_migration_test.sh`
4. 构建项目: `cd build && cmake .. && make`
5. 运行网关测试: `./tests/test_gateway.sh`
6. 查看迁移总结: `doc/TECH_STACK_MIGRATION_SUMMARY.md`

---

**更新日期**: 2024-12-06
