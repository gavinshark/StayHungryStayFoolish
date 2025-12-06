#include "http_client.hpp"
#include "http_parser.hpp"
#include "logger.hpp"
#include <sstream>

namespace gateway {

// RequestContext implementation
HttpClient::RequestContext::RequestContext(
    asio::io_context& io_context,
    const UrlInfo& url_info,
    const HttpRequest& request,
    ResponseCallback callback,
    std::chrono::milliseconds timeout)
    : io_context_(io_context)
    , socket_(io_context)
    , resolver_(io_context)
    , timeout_timer_(io_context)
    , url_info_(url_info)
    , request_(request)
    , callback_(callback)
    , timeout_(timeout)
{
}

void HttpClient::RequestContext::start() {
    // 启动超时定时器
    timeout_timer_.expires_after(timeout_);
    timeout_timer_.async_wait(
        [self = shared_from_this()](const std::error_code& ec) {
            self->handle_timeout(ec);
        });
    
    do_resolve();
}

void HttpClient::RequestContext::do_resolve() {
    auto self(shared_from_this());
    
    Logger::debug("Resolving {}:{}", url_info_.host, url_info_.port);
    
    resolver_.async_resolve(
        url_info_.host, url_info_.port,
        [this, self](std::error_code ec, 
                     asio::ip::tcp::resolver::results_type endpoints) {
            if (completed_) return;
            
            if (!ec) {
                Logger::debug("Resolved {} to {} endpoints", 
                            url_info_.host, endpoints.size());
                do_connect(endpoints);
            } else {
                Logger::error("Resolve failed: {}", ec.message());
                cancel_timeout();
                callback_(ec, HttpResponse::make_502());
                completed_ = true;
            }
        });
}

void HttpClient::RequestContext::do_connect(
    const asio::ip::tcp::resolver::results_type& endpoints)
{
    auto self(shared_from_this());
    
    Logger::debug("Connecting to {}:{}", url_info_.host, url_info_.port);
    
    asio::async_connect(
        socket_, endpoints,
        [this, self](std::error_code ec, 
                     const asio::ip::tcp::endpoint& /*endpoint*/) {
            if (completed_) return;
            
            if (!ec) {
                Logger::debug("Connected to {}:{}", 
                            url_info_.host, url_info_.port);
                do_write();
            } else {
                Logger::error("Connect failed: {}", ec.message());
                cancel_timeout();
                callback_(ec, HttpResponse::make_502());
                completed_ = true;
            }
        });
}

void HttpClient::RequestContext::do_write() {
    auto self(shared_from_this());
    
    // 构建HTTP请求
    std::string request_str = request_.to_string();
    
    Logger::debug("Sending request ({} bytes)", request_str.size());
    
    asio::async_write(
        socket_, asio::buffer(request_str),
        [this, self](std::error_code ec, std::size_t /*bytes_transferred*/) {
            if (completed_) return;
            
            if (!ec) {
                Logger::debug("Request sent");
                do_read();
            } else {
                Logger::error("Write failed: {}", ec.message());
                cancel_timeout();
                callback_(ec, HttpResponse::make_502());
                completed_ = true;
            }
        });
}

void HttpClient::RequestContext::do_read() {
    auto self(shared_from_this());
    
    // 读取响应头（直到\r\n\r\n）
    asio::async_read_until(
        socket_, response_buffer_, "\r\n\r\n",
        [this, self](std::error_code ec, std::size_t bytes_transferred) {
            if (completed_) return;
            
            if (!ec) {
                // 读取所有可用数据
                std::istream is(&response_buffer_);
                std::ostringstream oss;
                oss << is.rdbuf();
                response_data_ = oss.str();
                
                Logger::debug("Response received ({} bytes)", response_data_.size());
                
                try {
                    // 解析响应
                    HttpResponse response = HttpParser::parse_response(response_data_);
                    
                    cancel_timeout();
                    callback_(std::error_code(), response);
                    completed_ = true;
                    
                } catch (const std::exception& e) {
                    Logger::error("Parse response failed: {}", e.what());
                    cancel_timeout();
                    callback_(std::make_error_code(std::errc::protocol_error),
                            HttpResponse::make_502());
                    completed_ = true;
                }
            } else if (ec == asio::error::eof) {
                // 连接关闭，尝试解析已接收的数据
                std::istream is(&response_buffer_);
                std::ostringstream oss;
                oss << is.rdbuf();
                response_data_ += oss.str();
                
                try {
                    HttpResponse response = HttpParser::parse_response(response_data_);
                    cancel_timeout();
                    callback_(std::error_code(), response);
                    completed_ = true;
                } catch (const std::exception& e) {
                    Logger::error("Parse response failed: {}", e.what());
                    cancel_timeout();
                    callback_(std::make_error_code(std::errc::protocol_error),
                            HttpResponse::make_502());
                    completed_ = true;
                }
            } else {
                Logger::error("Read failed: {}", ec.message());
                cancel_timeout();
                callback_(ec, HttpResponse::make_502());
                completed_ = true;
            }
        });
}

void HttpClient::RequestContext::handle_timeout(const std::error_code& ec) {
    if (!ec && !completed_) {
        Logger::error("Request timeout");
        
        // 关闭socket以取消所有操作
        std::error_code ignored_ec;
        socket_.close(ignored_ec);
        
        callback_(std::make_error_code(std::errc::timed_out),
                HttpResponse::make_504());
        completed_ = true;
    }
}

void HttpClient::RequestContext::cancel_timeout() {
    std::error_code ec;
    timeout_timer_.cancel(ec);
}

// HttpClient implementation
HttpClient::HttpClient(asio::io_context& io_context)
    : io_context_(io_context)
{
}

void HttpClient::async_request(
    const std::string& url,
    const HttpRequest& request,
    ResponseCallback callback,
    std::chrono::milliseconds timeout)
{
    try {
        auto url_info = parse_url(url);
        
        auto context = std::make_shared<RequestContext>(
            io_context_, url_info, request, callback, timeout);
        
        context->start();
        
    } catch (const std::exception& e) {
        Logger::error("Failed to create request: {}", e.what());
        callback(std::make_error_code(std::errc::invalid_argument),
                HttpResponse::make_502());
    }
}

HttpClient::UrlInfo HttpClient::parse_url(const std::string& url) {
    UrlInfo info;
    
    // 简化的URL解析
    // 格式: http://host:port/path
    size_t protocol_end = url.find("://");
    if (protocol_end == std::string::npos) {
        throw std::runtime_error("Invalid URL: missing protocol");
    }
    
    size_t host_start = protocol_end + 3;
    size_t port_start = url.find(':', host_start);
    size_t path_start = url.find('/', host_start);
    
    if (port_start != std::string::npos && 
        (path_start == std::string::npos || port_start < path_start)) {
        // 有端口号
        info.host = url.substr(host_start, port_start - host_start);
        
        size_t port_end = (path_start != std::string::npos) ? path_start : url.length();
        info.port = url.substr(port_start + 1, port_end - port_start - 1);
    } else {
        // 没有端口号，使用默认端口80
        size_t host_end = (path_start != std::string::npos) ? path_start : url.length();
        info.host = url.substr(host_start, host_end - host_start);
        info.port = "80";
    }
    
    if (path_start != std::string::npos) {
        info.path = url.substr(path_start);
    } else {
        info.path = "/";
    }
    
    return info;
}

} // namespace gateway
