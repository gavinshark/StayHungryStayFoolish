#pragma once

#include "types.hpp"
#include <string>
#include <memory>
#include <iostream>
#include <fstream>
#include <mutex>
#include <sstream>
#include <ctime>

namespace gateway {

class Logger {
public:
    // 初始化日志系统
    static void init(const std::string& log_file, const std::string& log_level);
    
    // 日志方法
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warn(const std::string& message);
    static void error(const std::string& message);
    
    // 获取当前日志级别
    static LogLevel get_level();

private:
    static void log(LogLevel level, const std::string& message);
    static std::string level_to_string(LogLevel level);
    static LogLevel string_to_level(const std::string& level_str);
    static std::string get_timestamp();

    static LogLevel current_level_;
    static std::ofstream log_file_;
    static std::mutex mutex_;
    static bool initialized_;
};

} // namespace gateway
