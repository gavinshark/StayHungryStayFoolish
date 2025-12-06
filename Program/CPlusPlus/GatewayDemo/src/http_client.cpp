#include "http_client.hpp"
#include "http_parser.hpp"
#include "logger.hpp"
#include <sstream>
#include <thread>
#include <vector>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/select.h>
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

#include <cstring>

namespace gateway {

void HttpClient::async_request(
    const std::string& url,
    const HttpRequest& request,
    std::function<void(std::error_code, HttpResponse)> callback,
    std::chrono::milliseconds timeout)
{
    // 在实际实现中，这应该是真正的异步操作
    // 这里为了演示，使用线程模拟异步
    std::thread([this, url, request, callback, timeout]() {
        try {
            auto url_info = parse_url(url);
            HttpResponse response = send_request_sync(
                url_info.host, url_info.port, request, timeout
            );
            callback(std::error_code(), response);
        } catch (const std::exception& e) {
            Logger::error("HTTP request failed: " + std::string(e.what()));
            callback(std::make_error_code(std::errc::connection_refused), 
                    HttpResponse::make_502());
        }
    }).detach();
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
        std::string port_str = url.substr(port_start + 1, port_end - port_start - 1);
        info.port = static_cast<uint16_t>(std::stoi(port_str));
    } else {
        // 没有端口号，使用默认端口80
        size_t host_end = (path_start != std::string::npos) ? path_start : url.length();
        info.host = url.substr(host_start, host_end - host_start);
        info.port = 80;
    }
    
    if (path_start != std::string::npos) {
        info.path = url.substr(path_start);
    } else {
        info.path = "/";
    }
    
    return info;
}

HttpResponse HttpClient::send_request_sync(
    const std::string& host, 
    uint16_t port,
    const HttpRequest& request, 
    std::chrono::milliseconds timeout)
{
    Logger::debug("Sending HTTP request to " + host + ":" + std::to_string(port) + request.path);
    
    // 1. 创建 socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        throw std::runtime_error("Failed to create socket");
    }
    
    // 2. 设置超时
    set_socket_timeout(sock, timeout);
    
    try {
        // 3. 解析主机名
        struct sockaddr_in server_addr{};
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
        
        // 尝试直接解析 IP 地址
        if (inet_pton(AF_INET, host.c_str(), &server_addr.sin_addr) != 1) {
            // 不是 IP 地址，需要 DNS 解析
            struct hostent* he = gethostbyname(host.c_str());
            if (he == nullptr) {
                throw std::runtime_error("Failed to resolve host: " + host);
            }
            memcpy(&server_addr.sin_addr, he->h_addr_list[0], he->h_length);
        }
        
        // 4. 连接到服务器
        if (connect(sock, reinterpret_cast<struct sockaddr*>(&server_addr), 
                   sizeof(server_addr)) == SOCKET_ERROR) {
            throw std::runtime_error("Failed to connect to " + host + ":" + std::to_string(port));
        }
        
        Logger::debug("Connected to " + host + ":" + std::to_string(port));
        
        // 5. 发送 HTTP 请求
        std::string request_str = request.to_string();
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
        
        Logger::debug("Request sent (" + std::to_string(total_sent) + " bytes)");
        
        // 6. 接收响应
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
            
            // 检查是否接收完整（简化版：检查是否有 Content-Length）
            if (is_response_complete(response_data)) {
                break;
            }
        }
        
        Logger::debug("Response received (" + std::to_string(response_data.length()) + " bytes)");
        
        // 7. 关闭 socket
        closesocket(sock);
        
        // 8. 解析响应
        HttpResponse response = HttpParser::parse_response(response_data);
        
        return response;
        
    } catch (...) {
        closesocket(sock);
        throw;
    }
}

void HttpClient::set_socket_timeout(int sock, std::chrono::milliseconds timeout) {
    int timeout_ms = static_cast<int>(timeout.count());
    
#ifdef _WIN32
    // Windows: 超时单位是毫秒
    DWORD timeout_val = timeout_ms;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, 
              reinterpret_cast<const char*>(&timeout_val), sizeof(timeout_val));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, 
              reinterpret_cast<const char*>(&timeout_val), sizeof(timeout_val));
#else
    // Linux/macOS: 超时使用 timeval 结构
    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
#endif
}

bool HttpClient::is_response_complete(const std::string& response_data) {
    // 查找响应头结束标记
    size_t header_end = response_data.find("\r\n\r\n");
    if (header_end == std::string::npos) {
        return false;  // 还没收到完整的头部
    }
    
    // 提取头部
    std::string headers = response_data.substr(0, header_end);
    
    // 查找 Content-Length
    size_t cl_pos = headers.find("Content-Length:");
    if (cl_pos == std::string::npos) {
        cl_pos = headers.find("content-length:");
    }
    
    if (cl_pos != std::string::npos) {
        // 找到 Content-Length，解析它
        size_t value_start = headers.find(':', cl_pos) + 1;
        size_t value_end = headers.find('\r', value_start);
        std::string length_str = headers.substr(value_start, value_end - value_start);
        
        // 去除空格
        length_str.erase(0, length_str.find_first_not_of(" \t"));
        length_str.erase(length_str.find_last_not_of(" \t") + 1);
        
        int content_length = std::stoi(length_str);
        int body_start = static_cast<int>(header_end + 4);
        int body_length = static_cast<int>(response_data.length()) - body_start;
        
        return body_length >= content_length;
    }
    
    // 如果没有 Content-Length，检查 Transfer-Encoding: chunked
    if (headers.find("Transfer-Encoding: chunked") != std::string::npos ||
        headers.find("transfer-encoding: chunked") != std::string::npos) {
        // 检查是否以 "0\r\n\r\n" 结尾（chunked 结束标记）
        return response_data.find("0\r\n\r\n", header_end) != std::string::npos;
    }
    
    // 如果既没有 Content-Length 也没有 chunked，假设连接关闭时响应完成
    return false;
}

} // namespace gateway
