#include "http_server.hpp"
#include "http_parser.hpp"
#include "logger.hpp"
#include <iostream>

namespace gateway {

// Connection implementation
HttpServer::Connection::Connection(
    asio::ip::tcp::socket socket,
    RequestHandler handler)
    : socket_(std::move(socket))
    , handler_(handler)
{
}

void HttpServer::Connection::start() {
    do_read();
}

void HttpServer::Connection::do_read() {
    auto self(shared_from_this());
    
    asio::async_read_until(socket_, buffer_, "\r\n\r\n",
        [this, self](std::error_code ec, std::size_t bytes_transferred) {
            if (!ec) {
                // 读取请求数据
                std::istream is(&buffer_);
                std::string line;
                std::ostringstream request_stream;
                
                // 读取所有数据
                while (std::getline(is, line)) {
                    request_stream << line << "\n";
                }
                
                request_data_ = request_stream.str();
                
                try {
                    // 解析HTTP请求
                    HttpRequest request = HttpParser::parse_request(request_data_);
                    
                    // 处理请求
                    HttpResponse response;
                    if (handler_) {
                        handler_(request, response);
                    } else {
                        response = HttpResponse::make_500();
                    }
                    
                    // 发送响应
                    do_write(response.to_string());
                    
                } catch (const std::exception& e) {
                    Logger::error("Error parsing request: {}", e.what());
                    HttpResponse error_response = HttpResponse::make_500();
                    do_write(error_response.to_string());
                }
            } else if (ec != asio::error::operation_aborted) {
                Logger::error("Read error: {}", ec.message());
            }
        });
}

void HttpServer::Connection::do_write(const std::string& response) {
    auto self(shared_from_this());
    
    asio::async_write(socket_, asio::buffer(response),
        [this, self](std::error_code ec, std::size_t /*bytes_transferred*/) {
            if (ec && ec != asio::error::operation_aborted) {
                Logger::error("Write error: {}", ec.message());
            }
            
            // 关闭连接
            std::error_code ignored_ec;
            socket_.shutdown(asio::ip::tcp::socket::shutdown_both, ignored_ec);
            socket_.close(ignored_ec);
        });
}

// HttpServer implementation
HttpServer::HttpServer(asio::io_context& io_context, uint16_t port)
    : io_context_(io_context)
    , acceptor_(io_context, asio::ip::tcp::endpoint(asio::ip::tcp::v4(), port))
    , port_(port)
{
}

HttpServer::~HttpServer() {
    stop();
}

void HttpServer::set_request_handler(RequestHandler handler) {
    request_handler_ = handler;
}

void HttpServer::start() {
    if (running_) {
        return;
    }
    
    running_ = true;
    do_accept();
    
    Logger::info("HTTP Server (Asio) started on port {}", port_);
}

void HttpServer::stop() {
    if (!running_) {
        return;
    }
    
    running_ = false;
    
    std::error_code ec;
    acceptor_.close(ec);
    
    Logger::info("HTTP Server (Asio) stopped");
}

void HttpServer::do_accept() {
    acceptor_.async_accept(
        [this](std::error_code ec, asio::ip::tcp::socket socket) {
            if (!ec) {
                // 创建新连接并启动
                auto conn = std::make_shared<Connection>(
                    std::move(socket), request_handler_);
                conn->start();
            } else if (ec != asio::error::operation_aborted) {
                Logger::error("Accept error: {}", ec.message());
            }
            
            // 继续接受下一个连接
            if (running_) {
                do_accept();
            }
        });
}

} // namespace gateway
