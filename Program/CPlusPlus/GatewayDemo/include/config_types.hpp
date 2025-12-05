#pragma once

#include "types.hpp"
#include <string>
#include <vector>

namespace gateway {

struct Route {
    std::string path_pattern;           // 路径模式，如 "/api/users"
    MatchType match_type;               // 匹配类型：EXACT 或 PREFIX
    std::vector<std::string> backends;  // 后端服务URL列表
    int priority;                       // 优先级，数值越小优先级越高

    // 用于排序的比较函数
    bool operator<(const Route& other) const {
        return priority < other.priority;
    }
};

struct GatewayConfig {
    uint16_t listen_port;               // 监听端口
    std::vector<Route> routes;          // 路由规则列表
    std::string log_level;              // 日志级别：debug, info, warn, error
    std::string log_file;               // 日志文件路径
    int backend_timeout_ms;             // 后端超时时间（毫秒）
    int client_timeout_ms;              // 客户端超时时间（毫秒）

    // 默认构造函数
    GatewayConfig()
        : listen_port(8080)
        , log_level("info")
        , log_file("gateway.log")
        , backend_timeout_ms(5000)
        , client_timeout_ms(30000)
    {}
};

} // namespace gateway
