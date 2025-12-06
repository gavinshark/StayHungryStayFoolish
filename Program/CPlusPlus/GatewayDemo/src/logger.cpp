#include "logger.hpp"
#include <algorithm>
#include <iomanip>
#include <sys/stat.h>
#include <sys/types.h>

#ifdef _WIN32
#include <direct.h>
#define mkdir(path, mode) _mkdir(path)
#endif

namespace gateway {

// 静态成员初始化
LogLevel Logger::current_level_ = LogLevel::INFO;
std::ofstream Logger::log_file_;
std::mutex Logger::mutex_;
bool Logger::initialized_ = false;

void Logger::init(const std::string& log_file, const std::string& log_level) {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        
        // 设置日志级别
        current_level_ = string_to_level(log_level);
        
        // 创建日志目录（如果需要）
        size_t last_slash = log_file.find_last_of("/\\");
        if (last_slash != std::string::npos) {
            std::string log_dir = log_file.substr(0, last_slash);
            // 尝试创建目录（如果已存在会失败，但不影响）
            mkdir(log_dir.c_str(), 0755);
        }
        
        // 打开日志文件
        log_file_.open(log_file, std::ios::app);
        if (!log_file_.is_open()) {
            std::cerr << "Warning: Failed to open log file: " << log_file << std::endl;
        }
        
        initialized_ = true;
    }  // 释放锁
    
    // 记录初始化信息（在锁外调用，避免死锁）
    info("Logger initialized with level: " + log_level);
}

void Logger::debug(const std::string& message) {
    log(LogLevel::DEBUG, message);
}

void Logger::info(const std::string& message) {
    log(LogLevel::INFO, message);
}

void Logger::warn(const std::string& message) {
    log(LogLevel::WARN, message);
}

void Logger::error(const std::string& message) {
    log(LogLevel::ERROR, message);
}

LogLevel Logger::get_level() {
    return current_level_;
}

void Logger::log(LogLevel level, const std::string& message) {
    // 检查日志级别
    if (level < current_level_) {
        return;
    }
    
    std::lock_guard<std::mutex> lock(mutex_);
    
    // 格式化日志消息
    std::ostringstream oss;
    oss << "[" << get_timestamp() << "] "
        << "[" << level_to_string(level) << "] "
        << message;
    
    std::string log_message = oss.str();
    
    // 输出到控制台
    std::cout << log_message << std::endl;
    
    // 输出到文件
    if (log_file_.is_open()) {
        log_file_ << log_message << std::endl;
        log_file_.flush();
    }
}

std::string Logger::level_to_string(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG: return "DEBUG";
        case LogLevel::INFO:  return "INFO";
        case LogLevel::WARN:  return "WARN";
        case LogLevel::ERROR: return "ERROR";
        default: return "UNKNOWN";
    }
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

std::string Logger::get_timestamp() {
    auto now = std::time(nullptr);
    auto tm = *std::localtime(&now);
    
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}

} // namespace gateway
