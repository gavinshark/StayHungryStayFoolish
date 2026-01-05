#include "gateway.hpp"
#include "config_manager.hpp"
#include "logger.hpp"
#include <iostream>
#include <csignal>
#include <atomic>

using namespace gateway;

// 全局变量用于信号处理
std::atomic<bool> shutdown_requested{false};
Gateway* g_gateway = nullptr;

// 信号处理函数
void signal_handler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        std::cout << "\nReceived shutdown signal..." << std::endl;
        shutdown_requested = true;
        
        if (g_gateway) {
            g_gateway->stop();
        }
    }
}

int main(int argc, char* argv[]) {
    try {
        // 默认配置文件路径
        std::string config_path = "config/config.json";
        
        // 从命令行参数读取配置文件路径
        if (argc > 1) {
            config_path = argv[1];
        }
        
        // 加载配置
        GatewayConfig config = ConfigManager::load_from_file(config_path);
        
        // 初始化日志系统
        Logger::init(config.log_file, config.log_level);
        
        // 打印启动信息
        Logger::info("=== Gateway Starting ===");
        Logger::info("Version: 2.1.0");
        Logger::info("Listen Port: {}", config.listen_port);
        Logger::info("Log Level: {}", config.log_level);
        Logger::info("Backend Timeout: {}ms", config.backend_timeout_ms);
        Logger::info("Routes configured: {}", config.routes.size());
        
        // 创建网关实例
        Gateway gateway(config, config_path);
        g_gateway = &gateway;
        
        // 注册信号处理
        std::signal(SIGINT, signal_handler);
        std::signal(SIGTERM, signal_handler);
        
        // 启动网关
        gateway.start();
        
        // 启用配置热重载
        gateway.enable_hot_reload();
        
        // 等待关闭信号
        while (!shutdown_requested && gateway.is_running()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        
        // 停止网关
        gateway.stop();
        gateway.disable_hot_reload();
        
        Logger::info("=== Gateway Stopped ===");
        
        return 0;
        
    } catch (const ConfigError& e) {
        std::cerr << "Configuration error: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }
}
