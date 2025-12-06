#include "gateway.hpp"
#include "config_manager.hpp"
#include "logger.hpp"
#include <condition_variable>
#include <mutex>

namespace gateway {

Gateway::Gateway(const GatewayConfig& config, const std::string& config_path)
    : config_path_(config_path)
    , config_(config)
    , server_(std::make_unique<HttpServer>(config.listen_port))
    , client_(std::make_unique<HttpClient>())
    , router_(std::make_unique<RequestRouter>())
    , load_balancer_(std::make_unique<LoadBalancer>(LoadBalancer::Strategy::ROUND_ROBIN))
{
    // 加载路由规则
    for (const auto& route : config_.routes) {
        router_->add_route(route);
    }
    
    // 设置请求处理器
    server_->set_request_handler(
        [this](const HttpRequest& req, HttpResponse& resp) {
            handle_request(req, resp);
        }
    );
    
    // 如果提供了配置文件路径，创建配置监控器
    if (!config_path_.empty()) {
        config_watcher_ = std::make_unique<ConfigWatcher>(config_path_);
    }
}

Gateway::~Gateway() {
    stop();
    disable_hot_reload();
}

void Gateway::start() {
    Logger::info("Starting Gateway on port " + std::to_string(config_.listen_port));
    server_->start();
}

void Gateway::stop() {
    Logger::info("Stopping Gateway");
    server_->stop();
}

bool Gateway::is_running() const {
    return server_->is_running();
}

void Gateway::handle_request(const HttpRequest& request, HttpResponse& response) {
    // 记录请求
    Logger::info("Request: " + request.method + " " + request.path);
    
    try {
        // 路由匹配
        auto route_opt = router_->match_route(request.path);
        if (!route_opt) {
            // 没有匹配的路由，返回404
            Logger::warn("No route matched for path: " + request.path);
            response = HttpResponse::make_404();
            Logger::info("Response: 404 Not Found");
            return;
        }
        
        const Route& route = *route_opt;
        
        // 负载均衡选择后端
        auto backend_opt = load_balancer_->select_backend(route.backends);
        if (!backend_opt) {
            // 所有后端都不可用，返回503
            Logger::error("All backends unavailable for route: " + route.path_pattern);
            response = HttpResponse::make_503();
            Logger::info("Response: 503 Service Unavailable");
            return;
        }
        
        std::string backend_url = *backend_opt;
        Logger::debug("Selected backend: " + backend_url);
        
        // 转发请求到后端（使用读取的超时配置）
        forward_request(request, backend_url, response);
        
        // 记录响应
        Logger::info("Response: " + std::to_string(response.status_code) + 
                    " " + response.status_message);
        
    } catch (const std::exception& e) {
        // 内部错误，返回500
        Logger::error("Internal error: " + std::string(e.what()));
        response = HttpResponse::make_500();
        Logger::info("Response: 500 Internal Server Error");
    }
}

void Gateway::forward_request(const HttpRequest& request,
                              const std::string& backend_url,
                              HttpResponse& response)
{
    // 读取超时配置
    int backend_timeout;
    {
        std::shared_lock<std::shared_mutex> config_lock(config_mutex_);
        backend_timeout = config_.backend_timeout_ms;
    }
    
    // 使用条件变量等待异步请求完成
    std::mutex mtx;
    std::condition_variable cv;
    bool completed = false;
    
    // 发送异步请求
    client_->async_request(
        backend_url + request.path,
        request,
        [&](std::error_code ec, HttpResponse backend_response) {
            std::lock_guard<std::mutex> lock(mtx);
            
            if (ec) {
                // 连接失败，标记后端不健康
                Logger::error("Backend request failed: " + backend_url);
                load_balancer_->mark_backend_unhealthy(backend_url);
                response = HttpResponse::make_502();
            } else {
                // 成功，复制响应
                response = backend_response;
            }
            
            completed = true;
            cv.notify_one();
        },
        std::chrono::milliseconds(backend_timeout)
    );
    
    // 等待请求完成（带超时）
    std::unique_lock<std::mutex> lock(mtx);
    if (!cv.wait_for(lock, std::chrono::milliseconds(backend_timeout + 1000),
                     [&]{ return completed; })) {
        // 超时
        Logger::error("Backend request timeout: " + backend_url);
        load_balancer_->mark_backend_unhealthy(backend_url);
        response = HttpResponse::make_504();
    }
}

void Gateway::reload_config(const std::string& config_path) {
    Logger::info("Reloading configuration from: " + config_path);
    
    try {
        // 加载新配置
        GatewayConfig new_config = ConfigManager::load_from_file(config_path);
        
        // 应用新配置
        apply_config(new_config);
        
        Logger::info("Configuration reloaded successfully");
    } catch (const std::exception& e) {
        Logger::error("Failed to reload configuration: " + std::string(e.what()));
        throw;
    }
}

void Gateway::apply_config(const GatewayConfig& new_config) {
    // 使用写锁更新配置（阻塞所有读取）
    std::unique_lock<std::shared_mutex> lock(config_mutex_);
    
    // 更新配置
    config_ = new_config;
    
    // 更新路由规则
    router_->clear_routes();
    for (const auto& route : config_.routes) {
        router_->add_route(route);
    }
    
    // 注意：这里不重启服务器，因为端口变更需要重启整个程序
    // 实际生产环境中，端口变更应该通过重启服务来实现
    if (new_config.listen_port != config_.listen_port) {
        Logger::warn("Listen port changed, but server restart is required to apply");
    }
    
    Logger::info("Configuration applied: " + std::to_string(config_.routes.size()) + " routes loaded");
}

void Gateway::enable_hot_reload() {
    if (!config_watcher_) {
        Logger::warn("Config watcher not initialized, cannot enable hot reload");
        return;
    }
    
    if (config_watcher_->is_running()) {
        Logger::warn("Hot reload already enabled");
        return;
    }
    
    // 启动配置监控
    config_watcher_->start([this](const std::string& path) {
        on_config_changed(path);
    });
    
    Logger::info("Hot reload enabled");
}

void Gateway::disable_hot_reload() {
    if (config_watcher_ && config_watcher_->is_running()) {
        config_watcher_->stop();
        Logger::info("Hot reload disabled");
    }
}

void Gateway::on_config_changed(const std::string& config_path) {
    Logger::info("Configuration file changed, reloading...");
    
    try {
        reload_config(config_path);
    } catch (const std::exception& e) {
        Logger::error("Failed to reload configuration after file change: " + std::string(e.what()));
    }
}

} // namespace gateway
