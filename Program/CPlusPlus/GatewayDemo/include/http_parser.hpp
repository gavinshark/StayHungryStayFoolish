#pragma once

#include "http_types.hpp"
#include <string>
#include <optional>
#include <stdexcept>

namespace gateway {

class HttpParseError : public std::runtime_error {
public:
    explicit HttpParseError(const std::string& message)
        : std::runtime_error(message) {}
};

class HttpParser {
public:
    // 解析HTTP请求
    static HttpRequest parse_request(const std::string& raw_request);
    
    // 解析HTTP响应
    static HttpResponse parse_response(const std::string& raw_response);

private:
    // 辅助函数：查找行结束符
    static size_t find_line_end(const std::string& str, size_t start);
    
    // 辅助函数：去除字符串两端空白
    static std::string trim(const std::string& str);
    
    // 辅助函数：分割字符串
    static std::pair<std::string, std::string> split_header(const std::string& line);
};

} // namespace gateway
