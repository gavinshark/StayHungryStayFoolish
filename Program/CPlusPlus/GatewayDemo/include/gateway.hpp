#pragma once

#include "http_server.hpp"
#include "http_client.hpp"
#include "request_router.hpp"
#include "load_balancer.hpp"
#include "config_types.hpp"
#include <memory>

namespace gateway {

class Gateway {
public:
    explicit Gateway(const GatewayConfig& config);
    ~Gateway();
    
    // 启动网关
    void start();
    
    // 停止网关
    void stop();
    
    // 检查是否正在运行
    bool is_running() const;

private:
    // 处理HTTP请求
    void handle_request(const HttpRequest& request, HttpResponse& response);
    
    // 转发请求到后端
    void forward_request(const HttpRequest& request, 
                        const std::string& backend_url,
                        HttpResponse& response);
    
    GatewayConfig config_;
    std::unique_ptr<HttpServer> server_;
    std::unique_ptr<HttpClient> client_;
    std::unique_ptr<RequestRouter> router_;
    std::unique_ptr<LoadBalancer> load_balancer_;
};

} // namespace gateway
