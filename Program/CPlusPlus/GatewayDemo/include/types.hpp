#pragma once

#include <string>
#include <map>
#include <vector>
#include <optional>
#include <memory>
#include <functional>
#include <chrono>

namespace gateway {

// 前向声明
struct HttpRequest;
struct HttpResponse;
struct Route;
struct GatewayConfig;

// 路由匹配类型
enum class MatchType {
    EXACT,   // 精确匹配
    PREFIX   // 前缀匹配
};

// 负载均衡策略
enum class LoadBalanceStrategy {
    ROUND_ROBIN
};

// 日志级别
enum class LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
};

} // namespace gateway
