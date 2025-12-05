#include "gateway.hpp"
#include "logger.hpp"
#include <condition_variable>
#include <mutex>

namespace gateway {

Gateway::Gateway(const GatewayConfig& config)
    : config_(config)
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
}

Gateway::~Gateway() {
    stop();
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
        
        // 转发请求到后端
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
        std::chrono::milliseconds(config_.backend_timeout_ms)
    );
    
    // 等待请求完成（带超时）
    std::unique_lock<std::mutex> lock(mtx);
    if (!cv.wait_for(lock, std::chrono::milliseconds(config_.backend_timeout_ms + 1000),
                     [&]{ return completed; })) {
        // 超时
        Logger::error("Backend request timeout: " + backend_url);
        load_balancer_->mark_backend_unhealthy(backend_url);
        response = HttpResponse::make_504();
    }
}

} // namespace gateway
