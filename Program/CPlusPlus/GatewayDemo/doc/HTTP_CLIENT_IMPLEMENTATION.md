# HTTP Client 真实实现

## 📋 改进说明

将 HttpClient 从模拟实现改为真正发起 HTTP 请求的实现。

## 🔄 改进前后对比

### 改进前（模拟实现）

```cpp
HttpResponse HttpClient::send_request_sync(...) {
    // 模拟网络延迟
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    
    // 返回一个模拟的成功响应
    HttpResponse response;
    response.version = "HTTP/1.1";
    response.status_code = 200;
    response.status_message = "OK";
    response.body = "Response from backend";  // 假数据
    
    return response;
}
```

**问题**:
- ❌ 不发起真实的网络请求
- ❌ 总是返回固定的响应
- ❌ 无法连接到真实的后端服务器

### 改进后（真实实现）

```cpp
HttpResponse HttpClient::send_request_sync(...) {
    // 1. 创建 socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    
    // 2. 设置超时
    set_socket_timeout(sock, timeout);
    
    // 3. DNS 解析主机名
    struct hostent* he = gethostbyname(host.c_str());
    
    // 4. 连接到服务器
    connect(sock, ...);
    
    // 5. 发送 HTTP 请求
    send(sock, request_str.c_str(), ...);
    
    // 6. 接收响应
    recv(sock, buffer.data(), ...);
    
    // 7. 解析响应
    HttpResponse response = HttpParser::parse_response(response_data);
    
    return response;
}
```

**优点**:
- ✅ 发起真实的 TCP 连接
- ✅ 发送真实的 HTTP 请求
- ✅ 接收真实的 HTTP 响应
- ✅ 支持超时控制
- ✅ 支持 DNS 解析

## 🔧 实现细节

### 1. Socket 创建和连接

```cpp
// 创建 TCP socket
int sock = socket(AF_INET, SOCK_STREAM, 0);

// 配置服务器地址
struct sockaddr_in server_addr{};
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(port);

// DNS 解析
struct hostent* he = gethostbyname(host.c_str());
memcpy(&server_addr.sin_addr, he->h_addr_list[0], he->h_length);

// 连接
connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr));
```

### 2. 超时设置

```cpp
void HttpClient::set_socket_timeout(int sock, std::chrono::milliseconds timeout) {
    int timeout_ms = static_cast<int>(timeout.count());
    
#ifdef _WIN32
    // Windows: 超时单位是毫秒
    DWORD timeout_val = timeout_ms;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, 
              reinterpret_cast<const char*>(&timeout_val), sizeof(timeout_val));
#else
    // Linux/macOS: 超时使用 timeval 结构
    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
#endif
}
```

**跨平台支持**:
- Windows: 使用 `DWORD` 类型，单位毫秒
- Linux/macOS: 使用 `timeval` 结构

### 3. 发送请求

```cpp
// 序列化 HTTP 请求
std::string request_str = request.to_string();

// 发送所有数据
int total_sent = 0;
int request_len = static_cast<int>(request_str.length());

while (total_sent < request_len) {
    int sent = send(sock, request_str.c_str() + total_sent, 
                  request_len - total_sent, 0);
    if (sent == SOCKET_ERROR) {
        throw std::runtime_error("Failed to send request");
    }
    total_sent += sent;
}
```

**特点**:
- 循环发送，确保所有数据都发送完成
- 错误处理

### 4. 接收响应

```cpp
std::string response_data;
std::vector<char> buffer(4096);

while (true) {
    int received = recv(sock, buffer.data(), buffer.size(), 0);
    
    if (received == SOCKET_ERROR) {
        throw std::runtime_error("Failed to receive response");
    }
    
    if (received == 0) {
        // 连接关闭
        break;
    }
    
    response_data.append(buffer.data(), received);
    
    // 检查是否接收完整
    if (is_response_complete(response_data)) {
        break;
    }
}
```

**特点**:
- 循环接收，直到响应完整
- 支持 Content-Length 检测
- 支持 chunked 编码检测

### 5. 响应完整性检测

```cpp
bool HttpClient::is_response_complete(const std::string& response_data) {
    // 1. 查找响应头结束标记
    size_t header_end = response_data.find("\r\n\r\n");
    if (header_end == std::string::npos) {
        return false;  // 还没收到完整的头部
    }
    
    // 2. 提取头部
    std::string headers = response_data.substr(0, header_end);
    
    // 3. 查找 Content-Length
    size_t cl_pos = headers.find("Content-Length:");
    if (cl_pos != std::string::npos) {
        // 解析 Content-Length
        int content_length = std::stoi(length_str);
        int body_length = response_data.length() - (header_end + 4);
        
        return body_length >= content_length;
    }
    
    // 4. 检查 Transfer-Encoding: chunked
    if (headers.find("Transfer-Encoding: chunked") != std::string::npos) {
        return response_data.find("0\r\n\r\n", header_end) != std::string::npos;
    }
    
    return false;
}
```

**支持的检测方式**:
- ✅ Content-Length 头部
- ✅ Transfer-Encoding: chunked
- ✅ 连接关闭

## 🌍 跨平台支持

### Windows

```cpp
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#endif
```

**特点**:
- 使用 Winsock2 API
- 需要链接 `ws2_32.lib`
- 超时使用 `DWORD` 类型

### Linux / macOS

```cpp
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <unistd.h>
#endif
```

**特点**:
- 使用 POSIX socket API
- 超时使用 `timeval` 结构
- 使用 `close()` 关闭 socket

## 📊 完整的请求流程

```
1. 解析 URL
   http://localhost:9001/api/users
   ↓
   host: localhost
   port: 9001
   path: /api/users

2. 创建 Socket
   socket(AF_INET, SOCK_STREAM, 0)

3. DNS 解析
   gethostbyname("localhost")
   ↓
   127.0.0.1

4. 连接服务器
   connect(sock, 127.0.0.1:9001)

5. 发送 HTTP 请求
   GET /api/users HTTP/1.1\r\n
   Host: localhost:9001\r\n
   \r\n

6. 接收响应
   HTTP/1.1 200 OK\r\n
   Content-Type: application/json\r\n
   Content-Length: 123\r\n
   \r\n
   {"message": "Hello"}

7. 解析响应
   HttpParser::parse_response()

8. 返回响应对象
```

## 🎯 测试验证

### 测试步骤

```bash
# 1. 编译项目
./make.sh

# 2. 启动测试后端
python3 tests/test_backend.py 9001 &

# 3. 启动网关
./output/gateway config/config.json &

# 4. 发送测试请求
curl http://localhost:8080/api/users
```

### 预期结果

```json
{
  "message": "Hello from test backend",
  "path": "/api/users",
  "method": "GET",
  "port": 9001
}
```

**说明**: 这是真实的后端响应，不是模拟数据！

### 日志验证

```bash
cat log/gateway.log
```

预期日志：

```
[2024-12-06 17:00:00] [INFO] Request: GET /api/users
[2024-12-06 17:00:00] [DEBUG] Selected backend: http://localhost:9001
[2024-12-06 17:00:00] [DEBUG] Sending HTTP request to localhost:9001/api/users
[2024-12-06 17:00:00] [DEBUG] Connected to localhost:9001
[2024-12-06 17:00:00] [DEBUG] Request sent (123 bytes)
[2024-12-06 17:00:00] [DEBUG] Response received (456 bytes)
[2024-12-06 17:00:00] [INFO] Response: 200 OK
```

## 🔍 错误处理

### 1. 连接失败

```cpp
if (connect(sock, ...) == SOCKET_ERROR) {
    throw std::runtime_error("Failed to connect to " + host);
}
```

**结果**: Gateway 返回 502 Bad Gateway

### 2. 发送失败

```cpp
if (sent == SOCKET_ERROR) {
    throw std::runtime_error("Failed to send request");
}
```

**结果**: Gateway 返回 502 Bad Gateway

### 3. 接收超时

```cpp
// 设置了 socket 超时
set_socket_timeout(sock, timeout);

// 超时后 recv 返回错误
if (received == SOCKET_ERROR) {
    throw std::runtime_error("Failed to receive response");
}
```

**结果**: Gateway 返回 504 Gateway Timeout

### 4. DNS 解析失败

```cpp
struct hostent* he = gethostbyname(host.c_str());
if (he == nullptr) {
    throw std::runtime_error("Failed to resolve host: " + host);
}
```

**结果**: Gateway 返回 502 Bad Gateway

## 💡 优化建议

### 当前实现

- ✅ 真实的 HTTP 请求
- ✅ 跨平台支持
- ✅ 超时控制
- ✅ 错误处理

### 未来改进

1. **使用 Asio 库**
   - 真正的异步 I/O
   - 更好的性能
   - 更简洁的代码

2. **连接池**
   - 复用 TCP 连接
   - 减少连接开销
   - 提高性能

3. **HTTP/2 支持**
   - 多路复用
   - 头部压缩
   - 服务器推送

4. **HTTPS 支持**
   - TLS/SSL 加密
   - 证书验证
   - 安全通信

## 📚 相关文件

- `src/http_client.cpp` - HTTP 客户端实现
- `include/http_client.hpp` - HTTP 客户端接口
- `src/http_parser.cpp` - HTTP 解析器
- `doc/GATEWAY_FLOW.md` - 网关请求流程

## 🎉 总结

### 改进内容

- ✅ 实现了真实的 TCP socket 连接
- ✅ 实现了真实的 HTTP 请求发送
- ✅ 实现了真实的 HTTP 响应接收
- ✅ 支持 DNS 解析
- ✅ 支持超时控制
- ✅ 跨平台支持（Windows、Linux、macOS）
- ✅ 完整的错误处理

### 测试验证

```bash
# 完整测试
./tests/test_gateway.sh

# 查看日志
cat log/gateway.log
```

现在 Gateway 可以真正地转发 HTTP 请求到后端服务器了！

---

**更新日期**: 2024-12-06  
**状态**: ✅ 完成并测试通过
