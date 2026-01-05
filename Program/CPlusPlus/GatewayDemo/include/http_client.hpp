#pragma once

#include "http_types.hpp"
#include <string>
#include <functional>
#include <memory>
#include <chrono>
#include <system_error>
#include <asio.hpp>

namespace gateway {

// HTTP客户端（使用Asio异步I/O）
class HttpClient : public std::enable_shared_from_this<HttpClient> {
public:
    using ResponseCallback = std::function<void(std::error_code, HttpResponse)>;
    
    explicit HttpClient(asio::io_context& io_context);
    
    // 异步发送HTTP请求
    void async_request(
        const std::string& url,
        const HttpRequest& request,
        ResponseCallback callback,
        std::chrono::milliseconds timeout = std::chrono::milliseconds(5000)
    );

private:
    // URL信息
    struct UrlInfo {
        std::string host;
        std::string port;
        std::string path;
    };
    
    // 请求上下文
    class RequestContext : public std::enable_shared_from_this<RequestContext> {
    public:
        RequestContext(
            asio::io_context& io_context,
            const UrlInfo& url_info,
            const HttpRequest& request,
            ResponseCallback callback,
            std::chrono::milliseconds timeout);
        
        void start();
        
    private:
        void do_resolve();
        void do_connect(const asio::ip::tcp::resolver::results_type& endpoints);
        void do_write();
        void do_read();
        void handle_timeout(const std::error_code& ec);
        void cancel_timeout();
        
        asio::io_context& io_context_;
        asio::ip::tcp::socket socket_;
        asio::ip::tcp::resolver resolver_;
        asio::steady_timer timeout_timer_;
        
        UrlInfo url_info_;
        HttpRequest request_;
        ResponseCallback callback_;
        std::chrono::milliseconds timeout_;
        
        asio::streambuf response_buffer_;
        std::string response_data_;
        bool completed_{false};
    };
    
    // 解析URL
    UrlInfo parse_url(const std::string& url);
    
    asio::io_context& io_context_;
};

} // namespace gateway
