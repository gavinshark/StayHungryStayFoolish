#pragma once

#include <string>
#include <map>
#include <sstream>

namespace gateway {

struct HttpRequest {
    std::string method;      // GET, POST, PUT, DELETE, etc.
    std::string path;        // /api/users
    std::string version;     // HTTP/1.1
    std::map<std::string, std::string> headers;
    std::string body;

    // 序列化为HTTP请求字符串
    std::string to_string() const {
        std::ostringstream oss;
        
        // 请求行
        oss << method << " " << path << " " << version << "\r\n";
        
        // 头部
        for (const auto& [key, value] : headers) {
            oss << key << ": " << value << "\r\n";
        }
        
        // 空行分隔头部和正文
        oss << "\r\n";
        
        // 正文
        if (!body.empty()) {
            oss << body;
        }
        
        return oss.str();
    }

    // 相等比较（用于测试）
    bool operator==(const HttpRequest& other) const {
        return method == other.method &&
               path == other.path &&
               version == other.version &&
               headers == other.headers &&
               body == other.body;
    }
};

struct HttpResponse {
    std::string version;         // HTTP/1.1
    int status_code;             // 200, 404, 500, etc.
    std::string status_message;  // OK, Not Found, Internal Server Error, etc.
    std::map<std::string, std::string> headers;
    std::string body;

    // 序列化为HTTP响应字符串
    std::string to_string() const {
        std::ostringstream oss;
        
        // 状态行
        oss << version << " " << status_code << " " << status_message << "\r\n";
        
        // 头部
        for (const auto& [key, value] : headers) {
            oss << key << ": " << value << "\r\n";
        }
        
        // 空行分隔头部和正文
        oss << "\r\n";
        
        // 正文
        if (!body.empty()) {
            oss << body;
        }
        
        return oss.str();
    }

    // 相等比较（用于测试）
    bool operator==(const HttpResponse& other) const {
        return version == other.version &&
               status_code == other.status_code &&
               status_message == other.status_message &&
               headers == other.headers &&
               body == other.body;
    }

    // 便捷构造函数
    static HttpResponse make_error(int code, const std::string& message) {
        HttpResponse response;
        response.version = "HTTP/1.1";
        response.status_code = code;
        response.status_message = message;
        response.headers["Content-Type"] = "text/plain";
        response.headers["Content-Length"] = std::to_string(message.length());
        response.body = message;
        return response;
    }

    static HttpResponse make_404() {
        return make_error(404, "Not Found");
    }

    static HttpResponse make_500() {
        return make_error(500, "Internal Server Error");
    }

    static HttpResponse make_502() {
        return make_error(502, "Bad Gateway");
    }

    static HttpResponse make_503() {
        return make_error(503, "Service Unavailable");
    }

    static HttpResponse make_504() {
        return make_error(504, "Gateway Timeout");
    }
};

} // namespace gateway
