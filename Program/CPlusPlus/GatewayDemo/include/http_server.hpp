#pragma once

#include "http_types.hpp"
#include <string>
#include <functional>
#include <memory>
#include <asio.hpp>

namespace gateway {

// HTTP服务器（使用Asio异步I/O）
class HttpServer : public std::enable_shared_from_this<HttpServer> {
public:
    using RequestHandler = std::function<void(const HttpRequest&, HttpResponse&)>;
    
    explicit HttpServer(asio::io_context& io_context, uint16_t port);
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
    // 异步接受连接
    void do_accept();
    
    // 处理客户端连接
    class Connection : public std::enable_shared_from_this<Connection> {
    public:
        Connection(asio::ip::tcp::socket socket, RequestHandler handler);
        
        void start();
        
    private:
        void do_read();
        void do_write(const std::string& response);
        
        asio::ip::tcp::socket socket_;
        RequestHandler handler_;
        asio::streambuf buffer_;
        std::string request_data_;
    };
    
    asio::io_context& io_context_;
    asio::ip::tcp::acceptor acceptor_;
    uint16_t port_;
    RequestHandler request_handler_;
    bool running_{false};
};

} // namespace gateway
