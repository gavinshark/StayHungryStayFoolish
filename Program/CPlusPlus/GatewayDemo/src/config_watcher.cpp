#include "config_watcher.hpp"
#include "logger.hpp"
#include <thread>

#ifdef _WIN32
#include <windows.h>
#include <sys/types.h>
#include <sys/stat.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace gateway {

ConfigWatcher::ConfigWatcher(const std::string& config_path)
    : config_path_(config_path)
    , last_mtime_(0)
    , running_(false)
    , check_interval_ms_(1000)  // 默认1秒检查一次
{
    // 获取初始修改时间
    last_mtime_ = get_file_mtime(config_path_);
}

ConfigWatcher::~ConfigWatcher() {
    stop();
}

void ConfigWatcher::start(ChangeCallback callback) {
    if (running_) {
        Logger::warn("ConfigWatcher already running");
        return;
    }
    
    callback_ = callback;
    running_ = true;
    
    // 启动监控线程
    watch_thread_ = std::thread(&ConfigWatcher::watch_thread, this);
    
    Logger::info("ConfigWatcher started for: " + config_path_);
}

void ConfigWatcher::stop() {
    if (!running_) {
        return;
    }
    
    running_ = false;
    
    // 等待线程结束
    if (watch_thread_.joinable()) {
        watch_thread_.join();
    }
    
    Logger::info("ConfigWatcher stopped");
}

bool ConfigWatcher::is_running() const {
    return running_;
}

void ConfigWatcher::set_check_interval(int interval_ms) {
    check_interval_ms_ = interval_ms;
}

std::time_t ConfigWatcher::get_file_mtime(const std::string& path) {
#ifdef _WIN32
    struct _stat file_stat;
    if (_stat(path.c_str(), &file_stat) == 0) {
        return file_stat.st_mtime;
    }
#else
    struct stat file_stat;
    if (stat(path.c_str(), &file_stat) == 0) {
        return file_stat.st_mtime;
    }
#endif
    return 0;
}

void ConfigWatcher::watch_thread() {
    Logger::debug("ConfigWatcher thread started");
    
    while (running_) {
        // 检查文件修改时间
        std::time_t current_mtime = get_file_mtime(config_path_);
        
        if (current_mtime > 0 && current_mtime != last_mtime_) {
            // 文件已修改
            Logger::info("Config file changed: " + config_path_);
            last_mtime_ = current_mtime;
            
            // 调用回调函数
            if (callback_) {
                try {
                    callback_(config_path_);
                } catch (const std::exception& e) {
                    Logger::error("Config reload callback failed: " + std::string(e.what()));
                }
            }
        }
        
        // 等待一段时间再检查
        std::this_thread::sleep_for(std::chrono::milliseconds(check_interval_ms_));
    }
    
    Logger::debug("ConfigWatcher thread stopped");
}

} // namespace gateway
