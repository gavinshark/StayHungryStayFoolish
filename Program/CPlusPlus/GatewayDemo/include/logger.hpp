#pragma once

#include "types.hpp"
#include <string>
#include <memory>

// 使用spdlog作为日志库
#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/rotating_file_sink.h>

namespace gateway {

class Logger {
public:
    // 初始化日志系统
    static void init(const std::string& log_file, const std::string& log_level);
    
    // 日志方法（使用模板支持格式化）
    template<typename... Args>
    static void debug(const std::string& fmt, Args&&... args) {
        spdlog::debug(fmt, std::forward<Args>(args)...);
    }
    
    template<typename... Args>
    static void info(const std::string& fmt, Args&&... args) {
        spdlog::info(fmt, std::forward<Args>(args)...);
    }
    
    template<typename... Args>
    static void warn(const std::string& fmt, Args&&... args) {
        spdlog::warn(fmt, std::forward<Args>(args)...);
    }
    
    template<typename... Args>
    static void error(const std::string& fmt, Args&&... args) {
        spdlog::error(fmt, std::forward<Args>(args)...);
    }
    
    // 兼容旧接口（不带格式化参数）
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warn(const std::string& message);
    static void error(const std::string& message);
    
    // 获取当前日志级别
    static LogLevel get_level();

private:
    static LogLevel string_to_level(const std::string& level_str);
    static spdlog::level::level_enum to_spdlog_level(LogLevel level);
    static LogLevel from_spdlog_level(spdlog::level::level_enum level);
    
    static bool initialized_;
};

} // namespace gateway
