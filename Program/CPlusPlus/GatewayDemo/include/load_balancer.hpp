#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <optional>
#include <atomic>
#include <mutex>

namespace gateway {

class LoadBalancer {
public:
    enum class Strategy {
        ROUND_ROBIN
    };
    
    explicit LoadBalancer(Strategy strategy = Strategy::ROUND_ROBIN);
    
    // 选择后端服务
    std::optional<std::string> select_backend(const std::vector<std::string>& backends);
    
    // 标记后端为不健康
    void mark_backend_unhealthy(const std::string& backend_url);
    
    // 标记后端为健康
    void mark_backend_healthy(const std::string& backend_url);
    
    // 检查后端是否健康
    bool is_backend_healthy(const std::string& backend_url) const;

private:
    Strategy strategy_;
    std::atomic<size_t> round_robin_index_{0};
    mutable std::mutex health_mutex_;
    std::unordered_map<std::string, bool> backend_health_;
};

} // namespace gateway
