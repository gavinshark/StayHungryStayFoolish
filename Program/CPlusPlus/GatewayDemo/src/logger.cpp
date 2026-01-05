#include "logger.hpp"
#include <algorithm>
#include <iostream>
#include <sys/stat.h>
#include <sys/types.h>

#ifdef _WIN32
#include <direct.h>
#define mkdir(path, mode) _mkdir(path)
#endif

namespace gateway {

// 静态成员初始化
bool Logger::initialized_ = false;

void Logger::init(const std::string& log_file, const std::string& log_level) {
    if (initialized_) {
        return;
    }
    
    try {
        // 创建日志目录（如果需要）
        size_t last_slash = log_file.find_last_of("/\\");
        if (last_slash != std::string::npos) {
            std::string log_dir = log_file.substr(0, last_slash);
            mkdir(log_dir.c_str(), 0755);
        }
        
        // 创建sinks
        auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
        console_sink->set_level(spdlog::level::trace);
        console_sink->set_pattern("[%Y-%m-%d %H:%M:%S] [%^%l%$] %v");
        
        // 创建rotating file sink (10MB, 3个文件)
        auto file_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
            log_file, 1024 * 1024 * 10, 3);
        file_sink->set_level(spdlog::level::trace);
        file_sink->set_pattern("[%Y-%m-%d %H:%M:%S] [%l] %v");
        
        // 创建logger
        std::vector<spdlog::sink_ptr> sinks{console_sink, file_sink};
        auto logger = std::make_shared<spdlog::logger>("gateway", sinks.begin(), sinks.end());
        
        // 设置日志级别
        LogLevel level = string_to_level(log_level);
        logger->set_level(to_spdlog_level(level));
        
        // 设置为默认logger
        spdlog::set_default_logger(logger);
        
        // 设置刷新策略（每条日志都刷新，确保不丢失）
        spdlog::flush_on(spdlog::level::info);
        
        initialized_ = true;
        
        spdlog::info("Logger initialized with level: {}", log_level);
    } catch (const spdlog::spdlog_ex& ex) {
        std::cerr << "Log initialization failed: " << ex.what() << std::endl;
        throw;
    }
}

// 兼容旧接口
void Logger::debug(const std::string& message) {
    spdlog::debug(message);
}

void Logger::info(const std::string& message) {
    spdlog::info(message);
}

void Logger::warn(const std::string& message) {
    spdlog::warn(message);
}

void Logger::error(const std::string& message) {
    spdlog::error(message);
}

LogLevel Logger::get_level() {
    if (!initialized_) {
        return LogLevel::INFO;
    }
    return from_spdlog_level(spdlog::get_level());
}

LogLevel Logger::string_to_level(const std::string& level_str) {
    std::string lower = level_str;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    
    if (lower == "debug") return LogLevel::DEBUG;
    if (lower == "info")  return LogLevel::INFO;
    if (lower == "warn")  return LogLevel::WARN;
    if (lower == "error") return LogLevel::ERROR;
    
    return LogLevel::INFO; // 默认
}

spdlog::level::level_enum Logger::to_spdlog_level(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG: return spdlog::level::debug;
        case LogLevel::INFO:  return spdlog::level::info;
        case LogLevel::WARN:  return spdlog::level::warn;
        case LogLevel::ERROR: return spdlog::level::err;
        default: return spdlog::level::info;
    }
}

LogLevel Logger::from_spdlog_level(spdlog::level::level_enum level) {
    switch (level) {
        case spdlog::level::debug: return LogLevel::DEBUG;
        case spdlog::level::info:  return LogLevel::INFO;
        case spdlog::level::warn:  return LogLevel::WARN;
        case spdlog::level::err:   return LogLevel::ERROR;
        default: return LogLevel::INFO;
    }
}

} // namespace gateway
