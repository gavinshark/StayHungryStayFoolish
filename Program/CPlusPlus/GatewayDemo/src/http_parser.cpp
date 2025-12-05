#include "http_parser.hpp"
#include <sstream>
#include <algorithm>

namespace gateway {

HttpRequest HttpParser::parse_request(const std::string& raw_request) {
    if (raw_request.empty()) {
        throw HttpParseError("Empty request");
    }

    HttpRequest request;
    size_t pos = 0;

    // 解析请求行
    size_t line_end = find_line_end(raw_request, pos);
    if (line_end == std::string::npos) {
        throw HttpParseError("Invalid request: no line ending found");
    }

    std::string request_line = raw_request.substr(pos, line_end - pos);
    pos = line_end + 2; // 跳过 \r\n

    // 解析方法、路径和版本
    std::istringstream request_stream(request_line);
    if (!(request_stream >> request.method >> request.path >> request.version)) {
        throw HttpParseError("Invalid request line");
    }

    // 解析头部
    while (pos < raw_request.length()) {
        line_end = find_line_end(raw_request, pos);
        if (line_end == std::string::npos) {
            break;
        }

        std::string line = raw_request.substr(pos, line_end - pos);
        pos = line_end + 2;

        // 空行表示头部结束
        if (line.empty()) {
            break;
        }

        // 解析头部字段
        auto [key, value] = split_header(line);
        if (!key.empty()) {
            request.headers[key] = value;
        }
    }

    // 解析正文
    if (pos < raw_request.length()) {
        request.body = raw_request.substr(pos);
    }

    return request;
}

HttpResponse HttpParser::parse_response(const std::string& raw_response) {
    if (raw_response.empty()) {
        throw HttpParseError("Empty response");
    }

    HttpResponse response;
    size_t pos = 0;

    // 解析状态行
    size_t line_end = find_line_end(raw_response, pos);
    if (line_end == std::string::npos) {
        throw HttpParseError("Invalid response: no line ending found");
    }

    std::string status_line = raw_response.substr(pos, line_end - pos);
    pos = line_end + 2;

    // 解析版本、状态码和状态消息
    std::istringstream status_stream(status_line);
    if (!(status_stream >> response.version >> response.status_code)) {
        throw HttpParseError("Invalid status line");
    }

    // 读取状态消息（可能包含空格）
    std::getline(status_stream, response.status_message);
    response.status_message = trim(response.status_message);

    // 解析头部
    while (pos < raw_response.length()) {
        line_end = find_line_end(raw_response, pos);
        if (line_end == std::string::npos) {
            break;
        }

        std::string line = raw_response.substr(pos, line_end - pos);
        pos = line_end + 2;

        // 空行表示头部结束
        if (line.empty()) {
            break;
        }

        // 解析头部字段
        auto [key, value] = split_header(line);
        if (!key.empty()) {
            response.headers[key] = value;
        }
    }

    // 解析正文
    if (pos < raw_response.length()) {
        response.body = raw_response.substr(pos);
    }

    return response;
}

size_t HttpParser::find_line_end(const std::string& str, size_t start) {
    size_t pos = str.find("\r\n", start);
    return pos;
}

std::string HttpParser::trim(const std::string& str) {
    size_t start = 0;
    size_t end = str.length();

    while (start < end && std::isspace(static_cast<unsigned char>(str[start]))) {
        ++start;
    }

    while (end > start && std::isspace(static_cast<unsigned char>(str[end - 1]))) {
        --end;
    }

    return str.substr(start, end - start);
}

std::pair<std::string, std::string> HttpParser::split_header(const std::string& line) {
    size_t colon_pos = line.find(':');
    if (colon_pos == std::string::npos) {
        return {"", ""};
    }

    std::string key = trim(line.substr(0, colon_pos));
    std::string value = trim(line.substr(colon_pos + 1));

    return {key, value};
}

} // namespace gateway
