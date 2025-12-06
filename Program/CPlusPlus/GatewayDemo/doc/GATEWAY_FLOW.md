_url,
                              HttpResponse& response)
{
    std::mutex mtx;
    std::condition_variable cv;
    bool completed = false;
    
    // 发送异步请求
    client_->async_request(
        backend_url + request.path,
        request,
        [&](std::error_code ec, HttpResponse backend_response) {
            if (ec) {
                response = HttpResponse::make_502();  // ← 错误响应
            } else {
                response = backend_response;  // ← 复制后端响应
            }
            completed = true;
            cv.notify_one();
        },
        timeout
    );
    
    // 等待请求完成
    if (!cv.wait_for(lock, timeout, [&]{ return completed; })) {
        response = HttpResponse::make_504();  // ← 超时响应
    }
}
```

**关键点**: 
- 使用条件变量等待异步请求完成
- 将后端响应复制到 `response` 参数
- 处理错误情况（502, 504）

### 4. HttpResponse::to_string

```cpp
std::string to_string() const {
    std::ostringstream oss;
    
    // 状态行
    oss << version << " " << status_code << " " << status_message << "\r\n";
    
    // 头部
    for (const auto& [key, value] : headers) {
        oss << key << ": " << value << "\r\n";
    }
    
    // 空行
    oss << "\r\n";
    
    // 正文
    if (!body.empty()) {
        oss << body;
    }
    
    return oss.str();
}
```

**关键点**: 将响应对象序列化为 HTTP 协议格式的字符串。

## 🎯 响应传递路径

```
后端响应
    ↓
HttpClient::async_request 回调
    ↓
response = backend_response  (复制)
    ↓
Gateway::forward_request 返回
    ↓
Gateway::handle_request 返回
    ↓
HttpServer::handle_client 中的 response 对象
    ↓
response.to_string()  (序列化)
    ↓
send(client_socket, ...)  (发送)
    ↓
客户端接收
```

## 📊 不同场景的响应

### 场景 1: 成功转发

```
客户端请求 → Gateway → 后端 (200 OK)
                ↓
客户端 ← 200 OK + 后端数据
```

**代码**:
```cpp
response = backend_response;  // 复制后端的完整响应
```

### 场景 2: 路由未找到

```
客户端请求 → Gateway (无匹配路由)
                ↓
客户端 ← 404 Not Found
```

**代码**:
```cpp
response = HttpResponse::make_404();
```

### 场景 3: 后端不可用

```
客户端请求 → Gateway → 后端 (全部不可用)
                ↓
客户端 ← 503 Service Unavailable
```

**代码**:
```cpp
response = HttpResponse::make_503();
```

### 场景 4: 后端连接失败

```
客户端请求 → Gateway → 后端 (连接失败)
                ↓
客户端 ← 502 Bad Gateway
```

**代码**:
```cpp
if (ec) {
    response = HttpResponse::make_502();
}
```

### 场景 5: 后端超时

```
客户端请求 → Gateway → 后端 (超时)
                ↓
客户端 ← 504 Gateway Timeout
```

**代码**:
```cpp
if (!cv.wait_for(...)) {
    response = HttpResponse::make_504();
}
```

## 🔍 验证响应返回

### 测试方法

```bash
# 1. 启动后端
python3 tests/test_backend.py 9001 &

# 2. 启动网关
./output/gateway config/config.json &

# 3. 发送请求并查看响应
curl -v http://localhost:8080/api/users
```

### 预期输出

```
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 123
< 
{
  "message": "Hello from test backend",
  "path": "/api/users",
  "method": "GET",
  "port": 9001
}
```

**说明**: 
- `<` 开头的是响应头
- 最后的 JSON 是响应体
- 这些都是从后端返回，经过 Gateway 转发给客户端的

## 💡 关键设计

### 1. 引用传递

```cpp
void handle_request(const HttpRequest& request, HttpResponse& response)
//                                                ↑ 引用参数
```

**优点**:
- 避免复制
- 直接修改响应对象
- 调用者能获取到修改后的值

### 2. 同步等待异步请求

```cpp
// 发送异步请求
client_->async_request(..., [&](ec, backend_response) {
    response = backend_response;  // 在回调中填充
    completed = true;
    cv.notify_one();
});

// 等待完成
cv.wait_for(lock, timeout, [&]{ return completed; });
```

**优点**:
- 异步请求提高性能
- 同步等待简化逻辑
- 超时控制

### 3. 错误处理

每个错误场景都有对应的 HTTP 状态码：

| 错误 | 状态码 | 说明 |
|------|--------|------|
| 路由未找到 | 404 | Not Found |
| 内部错误 | 500 | Internal Server Error |
| 后端连接失败 | 502 | Bad Gateway |
| 后端全部不可用 | 503 | Service Unavailable |
| 后端超时 | 504 | Gateway Timeout |

## 🎓 总结

### 问题答案

**Gateway forward request 之后需要回客户端返回结果！**

代码已经正确实现了完整的请求-响应循环：

1. ✅ 接收客户端请求
2. ✅ 转发到后端
3. ✅ 接收后端响应
4. ✅ **返回给客户端** ← 这一步已实现

### 实现方式

- 使用引用参数传递响应对象
- 在 `handle_client` 中调用 `send()` 发送响应
- 支持成功响应和各种错误响应

### 验证方法

```bash
# 完整测试
./tests/test_gateway.sh

# 查看日志
cat log/gateway.log
```

---

**创建日期**: 2024-12-06  
**状态**: ✅ 已验证
