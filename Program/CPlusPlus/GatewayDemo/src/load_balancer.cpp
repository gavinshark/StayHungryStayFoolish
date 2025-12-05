#include "load_balancer.hpp"

namespace gateway {

LoadBalancer::LoadBalancer(Strategy strategy)
    : strategy_(strategy) {
}

std::optional<std::string> LoadBalancer::select_backend(const std::vector<std::string>& backends) {
    if (backends.empty()) {
        return std::nullopt;
    }
    
    // 过滤出健康的后端
    std::vector<std::string> healthy_backends;
    {
        std::lock_guard<std::mutex> lock(health_mutex_);
        for (const auto& backend : backends) {
            // 如果后端未被标记或被标记为健康，则认为是健康的
            auto it = backend_health_.find(backend);
            if (it == backend_health_.end() || it->second) {
                healthy_backends.push_back(backend);
            }
        }
    }
    
    // 如果没有健康的后端，返回空
    if (healthy_backends.empty()) {
        return std::nullopt;
    }
    
    // 根据策略选择后端
    switch (strategy_) {
        case Strategy::ROUND_ROBIN: {
            // 轮询算法
            size_t index = round_robin_index_.fetch_add(1) % healthy_backends.size();
            return healthy_backends[index];
        }
        default:
            return healthy_backends[0];
    }
}

void LoadBalancer::mark_backend_unhealthy(const std::string& backend_url) {
    std::lock_guard<std::mutex> lock(health_mutex_);
    backend_health_[backend_url] = false;
}

void LoadBalancer::mark_backend_healthy(const std::string& backend_url) {
    std::lock_guard<std::mutex> lock(health_mutex_);
    backend_health_[backend_url] = true;
}

bool LoadBalancer::is_backend_healthy(const std::string& backend_url) const {
    std::lock_guard<std::mutex> lock(health_mutex_);
    auto it = backend_health_.find(backend_url);
    if (it == backend_health_.end()) {
        return true;  // 默认健康
    }
    return it->second;
}

} // namespace gateway
