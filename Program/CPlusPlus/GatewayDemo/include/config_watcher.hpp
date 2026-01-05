#pragma once

#include <string>
#include <functional>
#include <thread>
#include <atomic>
#include <chrono>
#include <sys/stat.h>

namespace gateway {

// 配置文件监控器
// 跨平台实现：使用轮询方式检测文件修改时间
class ConfigWatcher {
public:
    using ChangeCallback = std::function<void(const std::string&)>;
    
    explicit ConfigWatcher(const std::string& config_path);
    ~ConfigWatcher();
    
    // 启动监控
    void start(ChangeCallback callback);
    
    // 停止监控
    void stop();
    
    // 检查是否正在运行
    bool is_running() const;
    
    // 设置检查间隔（毫秒）
    void set_check_interval(int interval_ms);

private:
    // 获取文件修改时间
    std::time_t get_file_mtime(const std::string& path);
    
    // 监控线程函数
    void watch_thread();
    
    std::string config_path_;
    std::time_t last_mtime_;
    std::atomic<bool> running_;
    std::thread watch_thread_;
    ChangeCallback callback_;
    int check_interval_ms_;
};

} // namespace gateway
