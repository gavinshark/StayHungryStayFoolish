# 设计文档

## 概述

本文档描述了一个基于C++的跨平台简易网关程序的设计。该网关使用现代C++17标准，采用异步I/O模型处理并发连接，支持HTTP协议的请求转发、路由匹配和负载均衡功能。

核心设计目标：
- 跨平台兼容性（Windows、Linux、macOS）
- 高性能异步网络I/O
- 模块化和可扩展的架构
- 简单易用的配置管理

## 架构

### 整体架构

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
│  └────────────┬─────────────────┘  │
│               │                     │
│  ┌────────────▼─────────────────┐  │
│  │   Configuration Manager      │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │   Logger                     │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │ HTTP Request
       ▼
┌─────────────┐
│   Backend   │
│   Service   │
└─────────────┘
```

### 技术栈选择

- **网络库**: Asio (standalone) - 跨平台异步I/O库
- **JSON解析**: nlohmann/json - 现代C++ JSON库
- **日志库**: spdlog - 快速的C++日志库
- **构建系统**: CMake - 跨平台构建工具
- **HTTP解析**: 自实现简单HTTP解析器或使用http-parser

## 组件和接口

### 1. HTTP Server (Listener)

负责监听客户端连接并接收HTTP请求。

```cpp
class HttpServer {
public:
    HttpServer(asio::io_context& io_context, uint16_t port);
    void start();
    void stop();
    void set_request_handler(std::function<void(HttpRequest, HttpResponse)> handler);
    
private:
    void do_accept();
    void handle_connection(std::shared_ptr<TcpConnection> connection);
    
    asio::io_context& io_context_;
    asio::ip::tcp::acceptor acceptor_;
    std::function<void(HttpRequest, HttpResponse)> request_handler_;
};
```

### 2. Request Router

根据配置的路由规则匹配请求路径并选择目标后端服务。

```cpp
struct Route {
    std::string path_pattern;  // 路径模式
    MatchType match_type;      // EXACT or PREFIX
    std::vector<std::string> backend_urls;
    int priority;
};

class RequestRouter {
public:
    void add_route(const Route& route);
    std::optional<Route> match_route(const std::string& path) const;
    void clear_routes();
    
private:
    std::vector<Route> routes_;  // 按优先级排序
};
```

### 3. Load Balancer

在多个后端服务之间分配请求，支持健康检查。

```cpp
class LoadBalancer {
public:
    enum class Strategy {
        ROUND_ROBIN
    };
    
    LoadBalancer(Strategy strategy = Strategy::ROUND_ROBIN);
    std::optional<std::string> select_backend(const std::vector<std::string>& backends);
    void mark_backend_unhealthy(const std::string& backend_url);
    void mark_backend_healthy(const std::string& backend_url);
    
private:
    Strategy strategy_;
    std::unordered_map<std::string, bool> backend_health_;
    std::atomic<size_t> round_robin_index_{0};
};
```

### 4. HTTP Client (Forwarder)

将请求转发到后端服务并获取响应。

```cpp
class HttpClient {
public:
    HttpClient(asio::io_context& io_context);
    
    void async_request(
        const std::string& url,
        const HttpRequest& request,
        std::function<void(std::error_code, HttpResponse)> callback,
        std::chrono::milliseconds timeout = std::chrono::milliseconds(5000)
    );
    
private:
    asio::io_context& io_context_;
};
```

### 5. Configuration Manager

加载和管理网关配置。

```cpp
struct GatewayConfig {
    uint16_t listen_port;
    std::vector<Route> routes;
    std::string log_level;
    std::string log_file;
    int backend_timeout_ms;
    int client_timeout_ms;
};

class ConfigManager {
public:
    static GatewayConfig load_from_file(const std::string& config_path);
    static void validate_config(const GatewayConfig& config);
    
private:
    static GatewayConfig parse_json(const nlohmann::json& json_config);
};
```

### 6. Logger

统一的日志接口。

```cpp
class Logger {
public:
    static void init(const std::string& log_file, const std::string& log_level);
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warn(const std::string& message);
    static void error(const std::string& message);
    
private:
    static std::shared_ptr<spdlog::logger> logger_;
};
```

## 数据模型

### HttpRequest

```cpp
struct HttpRequest {
    std::string method;           // GET, POST, etc.
    std::string path;             // /api/users
    std::string version;          // HTTP/1.1
    std::map<std::string, std::string> headers;
    std::string body;
    
    std::string to_string() const;  // 序列化为HTTP请求字符串
};
```

### HttpResponse

```cpp
struct HttpResponse {
    int status_code;              // 200, 404, 500, etc.
    std::string status_message;   // OK, Not Found, etc.
    std::string version;          // HTTP/1.1
    std::map<std::string, std::string> headers;
    std::string body;
    
    std::string to_string() const;  // 序列化为HTTP响应字符串
};
```

### 配置文件格式

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
    },
    {
      "path_pattern": "/api/orders",
      "match_type": "exact",
      "priority": 2,
      "backends": [
        "http://localhost:9003"
      ]
    }
  ]
}
```


## 正确性属性

*属性是指在系统所有有效执行中都应该成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性反思

在分析了所有验收标准后，我们识别出以下可以合并或优化的属性：

- 属性3.3和4.1都涉及路由匹配和转发，可以合并为一个综合属性
- 属性3.5（保留头部和内容）是转发正确性的核心，其他转发属性可以基于此验证
- 属性4.4和4.5（前缀和精确匹配）可以合并为一个路由匹配算法属性
- 属性6.1、6.2、6.3涉及不同错误场景，但都是错误响应的特例，可以统一为错误处理属性

### 配置管理属性

**属性 1: 有效配置加载一致性**
*对于任何*有效的配置文件，加载后网关的运行参数应该与配置文件中指定的值完全一致
**验证需求: 2.1, 2.3**

**属性 2: 无效配置拒绝**
*对于任何*包含无效参数的配置文件（如负数端口、空后端列表等），配置验证器应该拒绝该配置并抛出错误
**验证需求: 2.2, 2.5**

**属性 3: 配置热重载不中断服务**
*对于任何*正在处理请求的网关实例，当配置更新时，已建立的连接应该继续完成，新连接应该使用新配置
**验证需求: 2.4**

### HTTP处理属性

**属性 4: HTTP解析往返一致性**
*对于任何*有效的HTTP请求，将其序列化为字符串后再解析，应该得到等价的HttpRequest对象
**验证需求: 3.2**

**属性 5: 请求转发保持不变性**
*对于任何*HTTP请求，从客户端到网关再到后端服务的转发过程中，所有HTTP头部和请求体内容应该保持不变
**验证需求: 3.5**

**属性 6: 响应转发保持不变性**
*对于任何*后端服务的HTTP响应，从后端到网关再到客户端的转发过程中，所有HTTP头部和响应体内容应该保持不变
**验证需求: 3.4**

**属性 7: 连接接受正确性**
*对于任何*配置的监听端口，当客户端向该端口发起连接时，网关应该成功接受该连接
**验证需求: 3.1**

### 路由匹配属性

**属性 8: 路由匹配正确性**
*对于任何*请求路径和路由规则集合，如果路径满足某个路由规则的匹配条件（前缀或精确匹配），则该路由应该被选中
**验证需求: 4.1, 4.4, 4.5**

**属性 9: 路由优先级顺序**
*对于任何*多个匹配同一请求的路由规则，应该选择优先级最高（数值最小）的路由
**验证需求: 4.2**

**属性 10: 无匹配路由返回404**
*对于任何*不匹配任何已配置路由规则的请求路径，网关应该返回404 Not Found响应
**验证需求: 4.3**

### 负载均衡属性

**属性 11: 轮询分配均匀性**
*对于任何*具有N个健康后端的路由，连续N个请求应该分别被分配到N个不同的后端（轮询顺序）
**验证需求: 5.2**

**属性 12: 请求分配到多后端**
*对于任何*配置了多个后端的路由，多个请求应该被分配到不同的后端实例
**验证需求: 5.1**

**属性 13: 不健康后端跳过**
*对于任何*被标记为不健康的后端，负载均衡器在选择后端时应该跳过它，选择下一个健康的后端
**验证需求: 5.3**

**属性 14: 全部不可用返回503**
*对于任何*路由，如果其所有后端都被标记为不健康，网关应该返回503 Service Unavailable响应
**验证需求: 5.4**

**属性 15: 健康状态追踪一致性**
*对于任何*后端服务，标记为不健康后查询其状态应该返回不健康，标记为健康后查询应该返回健康
**验证需求: 5.5**

### 错误处理属性

**属性 16: 连接失败错误响应**
*对于任何*后端连接失败的情况，网关应该返回5xx系列错误响应给客户端
**验证需求: 6.1**

**属性 17: 超时返回504**
*对于任何*后端响应超时的请求，网关应该返回504 Gateway Timeout响应
**验证需求: 6.2**

**属性 18: 内部错误返回500**
*对于任何*网关内部处理错误（如解析失败、路由错误等），网关应该返回500 Internal Server Error响应
**验证需求: 6.3**

**属性 19: 客户端断开资源清理**
*对于任何*客户端提前断开连接的情况，网关应该取消对应的后端请求并释放相关资源
**验证需求: 6.4**

**属性 20: 超时配置生效**
*对于任何*配置的超时时间，当连接时间超过该值时，网关应该主动断开连接
**验证需求: 6.5**

### 日志记录属性

**属性 21: 请求日志完整性**
*对于任何*处理的HTTP请求，日志中应该包含请求方法、路径和响应状态码
**验证需求: 7.2**

**属性 22: 错误日志详细性**
*对于任何*发生的错误，日志中应该包含错误类型、错误消息和相关上下文信息
**验证需求: 7.3**

**属性 23: 日志级别过滤**
*对于任何*配置的日志级别，只有该级别及以上的日志消息应该被输出
**验证需求: 7.4**

**属性 24: 日志多目标输出**
*对于任何*日志消息，它应该同时出现在控制台输出和日志文件中
**验证需求: 7.5**

## 错误处理

### 错误分类

1. **配置错误**
   - 配置文件不存在或格式错误
   - 配置参数无效（如端口超出范围）
   - 处理方式：启动时验证，失败则终止并记录详细错误

2. **网络错误**
   - 后端连接失败
   - 连接超时
   - 处理方式：返回适当的HTTP错误码（502, 504），记录错误日志

3. **协议错误**
   - HTTP请求格式错误
   - 不支持的HTTP方法或版本
   - 处理方式：返回400 Bad Request，记录警告日志

4. **资源错误**
   - 内存分配失败
   - 文件描述符耗尽
   - 处理方式：拒绝新连接，返回503，记录严重错误

### 错误响应映射

| 错误类型 | HTTP状态码 | 说明 |
|---------|-----------|------|
| 路由未找到 | 404 | Not Found |
| 请求格式错误 | 400 | Bad Request |
| 后端连接失败 | 502 | Bad Gateway |
| 所有后端不可用 | 503 | Service Unavailable |
| 后端响应超时 | 504 | Gateway Timeout |
| 内部处理错误 | 500 | Internal Server Error |

### 资源清理策略

- 使用RAII模式管理所有资源（连接、内存、文件句柄）
- 异常安全保证：基本保证（不泄漏资源）
- 连接对象使用shared_ptr管理生命周期
- 超时定时器自动取消机制

## 测试策略

### 单元测试

单元测试用于验证各个组件的具体功能：

1. **配置管理测试**
   - 测试有效配置文件的加载
   - 测试各种无效配置的拒绝（空端口、无效JSON等）
   - 测试配置验证逻辑的边界情况

2. **路由匹配测试**
   - 测试精确匹配的特定路径
   - 测试前缀匹配的特定路径
   - 测试优先级排序的特定场景
   - 测试无匹配路由的情况

3. **HTTP解析测试**
   - 测试标准HTTP请求的解析
   - 测试边界情况（空头部、大请求体）
   - 测试格式错误的请求

4. **负载均衡测试**
   - 测试轮询算法的特定序列
   - 测试健康检查标记功能
   - 测试单后端和多后端场景

### 属性测试

属性测试用于验证系统在各种输入下的通用正确性：

**测试框架选择**: 使用 **RapidCheck** - 一个成熟的C++属性测试库，支持自动生成测试数据和收缩失败案例。

**配置要求**:
- 每个属性测试应该运行至少100次迭代
- 每个属性测试必须使用注释标记对应的设计文档属性
- 标记格式: `// Feature: cpp-gateway, Property X: [属性描述]`

**测试生成器**:
- HTTP请求生成器：生成各种有效的HTTP请求（不同方法、头部、路径）
- 配置生成器：生成有效和无效的配置对象
- 路由规则生成器：生成各种路由模式和优先级组合
- 后端URL生成器：生成有效的后端服务地址

**关键属性测试**:

1. **配置往返测试** (属性1)
   - 生成随机有效配置，加载后验证所有字段匹配

2. **HTTP解析往返测试** (属性4)
   - 生成随机HTTP请求对象，序列化后再解析，验证等价性

3. **路由匹配正确性测试** (属性8)
   - 生成随机路径和路由规则，验证匹配逻辑

4. **负载均衡轮询测试** (属性11)
   - 生成N个后端，发送N个请求，验证每个后端被访问一次

5. **请求转发不变性测试** (属性5)
   - 生成随机请求，模拟转发过程，验证内容不变

6. **错误响应正确性测试** (属性16-18)
   - 模拟各种错误场景，验证返回正确的HTTP状态码

### 集成测试

集成测试验证组件间的协作：

1. **端到端请求流程**
   - 启动网关和模拟后端
   - 发送HTTP请求，验证完整的转发流程
   - 验证日志记录正确

2. **负载均衡集成**
   - 配置多个后端
   - 发送多个请求，验证分配到不同后端
   - 模拟后端故障，验证故障转移

3. **配置热重载**
   - 在处理请求时更新配置文件
   - 验证新请求使用新配置，旧请求正常完成

### 测试工具

- **单元测试框架**: Google Test (gtest)
- **属性测试框架**: RapidCheck
- **HTTP模拟**: 自实现简单的HTTP服务器和客户端用于测试
- **异步测试**: 使用Asio的io_context进行异步操作测试

## 性能考虑

### 并发模型

- 使用Asio的异步I/O模型，单线程事件循环
- 可选的多线程模式：多个io_context实例，每个运行在独立线程
- 避免阻塞操作，所有I/O都是异步的

### 内存管理

- 使用对象池复用HTTP请求/响应对象
- 连接对象使用shared_ptr，自动管理生命周期
- 避免不必要的内存拷贝，使用移动语义

### 优化策略

- 路由匹配使用前缀树（Trie）优化查找性能
- 配置热重载使用读写锁，最小化锁竞争
- HTTP解析使用零拷贝技术，直接在接收缓冲区解析

## 部署考虑

### 构建产物

- 单一可执行文件
- 配置文件（config.json）
- 启动脚本（支持systemd/launchd）

### 运行要求

- C++17兼容的运行时库
- 最小内存：64MB
- 推荐内存：256MB+
- 无特殊权限要求（非特权端口）

### 监控指标

- 活跃连接数
- 请求处理速率（QPS）
- 后端健康状态
- 错误率统计
- 平均响应时间

## 扩展性

### 未来可能的扩展

1. **更多负载均衡策略**
   - 最少连接
   - 加权轮询
   - 一致性哈希

2. **高级路由功能**
   - 基于HTTP头部的路由
   - 正则表达式路径匹配
   - 路由重写

3. **安全功能**
   - TLS/SSL支持
   - 请求限流
   - IP黑白名单

4. **可观测性**
   - Prometheus指标导出
   - 分布式追踪（OpenTelemetry）
   - 健康检查端点

### 插件机制

预留插件接口，支持：
- 自定义请求/响应处理器
- 自定义负载均衡策略
- 自定义认证/授权逻辑
