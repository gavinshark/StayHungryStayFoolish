#pragma once

#include "http_server.hpp"
#include "http_client.hpp"
#include "request_router.hpp"
#include "load_balancer.hpp"
#include "config_types.hpp"
#include "config_watcher.hpp"
#include <memory>
#include <shared_mutex>

namespace gateway {

class Gateway {
public:
    explicit Gateway(const GatewayConfig& config, const std::string& config_path = "");
    ~Gateway();
    
    // 启动网关
    void start();
    
    // 停止网关
    void stop();
    
    // 检查是否正在运行
    bool is_running() const;
    
    // 重新加载配置
    void reload_config(const std::string& config_path);
    
    // 启用配置热重载
    void enable_hot_reload();
    
    // 禁用配置热重载
    void disable_hot_reload();

private:
    // 处理HTTP请求
    void handle_request(const HttpRequest& request, HttpResponse& response);
    
    // 转发请求到后端
    void forward_request(const HttpRequest& request, 
                        const std::string& backend_url,
                        HttpResponse& response);
    
    // 配置变更回调
    void on_config_changed(const std::string& config_path);
    
    // 应用新配置
    void apply_config(const GatewayConfig& new_config);
    
    std::string config_path_;
    GatewayConfig config_;
    mutable std::shared_mutex config_mutex_;  // 读写锁保护配置
    
    std::unique_ptr<HttpServer> server_;
    std::unique_ptr<HttpClient> client_;
    std::unique_ptr<RequestRouter> router_;
    std::unique_ptr<LoadBalancer> load_balancer_;
    std::unique_ptr<ConfigWatcher> config_watcher_;
};

} // namespace gateway
