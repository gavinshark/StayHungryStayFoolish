#pragma once

#include "http_types.hpp"
#include <string>
#include <functional>
#include <memory>
#include <thread>
#include <atomic>

namespace gateway {

// 简化的HTTP服务器实现
// 实际项目中应使用Asio进行异步I/O
class HttpServer {
public:
    using RequestHandler = std::function<void(const HttpRequest&, HttpResponse&)>;
    
    explicit HttpServer(uint16_t port);
    ~HttpServer();
    
    // 设置请求处理器
    void set_request_handler(RequestHandler handler);
    
    // 启动服务器
    void start();
    
    // 停止服务器
    void stop();
    
    // 检查是否正在运行
    bool is_running() const { return running_; }

private:
    void run();
    void handle_client(int client_socket);
    
    uint16_t port_;
    RequestHandler request_handler_;
    std::atomic<bool> running_{false};
    std::unique_ptr<std::thread> server_thread_;
    int server_socket_{-1};
};

} // namespace gateway
