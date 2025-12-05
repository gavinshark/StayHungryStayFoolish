#include "http_server.hpp"
#include "http_parser.hpp"
#include "logger.hpp"

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

#include <cstring>
#include <vector>

namespace gateway {

HttpServer::HttpServer(uint16_t port)
    : port_(port) {
#ifdef _WIN32
    WSADATA wsa_data;
    WSAStartup(MAKEWORD(2, 2), &wsa_data);
#endif
}

HttpServer::~HttpServer() {
    stop();
#ifdef _WIN32
    WSACleanup();
#endif
}

void HttpServer::set_request_handler(RequestHandler handler) {
    request_handler_ = handler;
}

void HttpServer::start() {
    if (running_) {
        return;
    }
    
    running_ = true;
    server_thread_ = std::make_unique<std::thread>(&HttpServer::run, this);
    
    Logger::info("HTTP Server started on port " + std::to_string(port_));
}

void HttpServer::stop() {
    if (!running_) {
        return;
    }
    
    running_ = false;
    
    if (server_socket_ != INVALID_SOCKET) {
        closesocket(server_socket_);
        server_socket_ = INVALID_SOCKET;
    }
    
    if (server_thread_ && server_thread_->joinable()) {
        server_thread_->join();
    }
    
    Logger::info("HTTP Server stopped");
}

void HttpServer::run() {
    // 创建socket
    server_socket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket_ == INVALID_SOCKET) {
        Logger::error("Failed to create socket");
        return;
    }
    
    // 设置socket选项
    int opt = 1;
#ifdef _WIN32
    setsockopt(server_socket_, SOL_SOCKET, SO_REUSEADDR, 
               reinterpret_cast<const char*>(&opt), sizeof(opt));
#else
    setsockopt(server_socket_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
    
    // 绑定地址
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port_);
    
    if (bind(server_socket_, reinterpret_cast<sockaddr*>(&address), 
             sizeof(address)) == SOCKET_ERROR) {
        Logger::error("Failed to bind socket to port " + std::to_string(port_));
        closesocket(server_socket_);
        return;
    }
    
    // 监听
    if (listen(server_socket_, 10) == SOCKET_ERROR) {
        Logger::error("Failed to listen on socket");
        closesocket(server_socket_);
        return;
    }
    
    Logger::info("Server listening on port " + std::to_string(port_));
    
    // 接受连接
    while (running_) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        
        int client_socket = accept(server_socket_, 
                                   reinterpret_cast<sockaddr*>(&client_addr), 
                                   &client_len);
        
        if (client_socket == INVALID_SOCKET) {
            if (running_) {
                Logger::warn("Failed to accept connection");
            }
            continue;
        }
        
        // 在新线程中处理客户端请求
        std::thread(&HttpServer::handle_client, this, client_socket).detach();
    }
}

void HttpServer::handle_client(int client_socket) {
    try {
        // 读取请求
        std::vector<char> buffer(4096);
        int bytes_received = recv(client_socket, buffer.data(), buffer.size() - 1, 0);
        
        if (bytes_received <= 0) {
            closesocket(client_socket);
            return;
        }
        
        buffer[bytes_received] = '\0';
        std::string raw_request(buffer.data(), bytes_received);
        
        // 解析请求
        HttpRequest request = HttpParser::parse_request(raw_request);
        
        // 处理请求
        HttpResponse response;
        if (request_handler_) {
            request_handler_(request, response);
        } else {
            response = HttpResponse::make_500();
        }
        
        // 发送响应
        std::string response_str = response.to_string();
        send(client_socket, response_str.c_str(), response_str.length(), 0);
        
    } catch (const std::exception& e) {
        Logger::error("Error handling client: " + std::string(e.what()));
        
        // 发送500错误
        HttpResponse error_response = HttpResponse::make_500();
        std::string response_str = error_response.to_string();
        send(client_socket, response_str.c_str(), response_str.length(), 0);
    }
    
    closesocket(client_socket);
}

} // namespace gateway
