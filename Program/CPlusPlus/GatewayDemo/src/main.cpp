#include "gateway.hpp"
#include "config_manager.hpp"
#include "logger.hpp"
#include <iostream>
#include <csignal>
#include <atomic>

using namespace gateway;

// 全局变量用于信号处理
std::atomic<bool> g_running{true};
Gateway* g_gateway = nullptr;

// 信号处理函数
void signal_handler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        std::cout << "\nReceived shutdown signal..." << std::endl;
        g_running = false;
        if (g_gateway) {
            g_gateway->stop();
        }
    }
}

int main(int argc, char* argv[]) {
    try {
        // 解析命令行参数
        std::string config_file = "config/config.json";
        if (argc > 1) {
            config_file = argv[1];
        }
        
        std::cout << "C++ Gateway v1.0.0" << std::endl;
        std::cout << "Loading configuration from: " << config_file << std::endl;
        
        // 加载配置
        GatewayConfig config = ConfigManager::load_from_file(config_file);
        
        // 初始化日志系统
        Logger::init(config.log_file, config.log_level);
        Logger::info("=== Gateway Starting ===");
        Logger::info("Version: 1.0.0");
        Logger::info("Listen Port: " + std::to_string(config.listen_port));
        Logger::info("Log Level: " + config.log_level);
        Logger::info("Backend Timeout: " + std::to_string(config.backend_timeout_ms) + "ms");
        Logger::info("Routes configured: " + std::to_string(config.routes.size()));
        
        // 创建并启动网关
        Gateway gateway(config);
        g_gateway = &gateway;
        
        // 注册信号处理
        std::signal(SIGINT, signal_handler);
        std::signal(SIGTERM, signal_handler);
        
        // 启动网关
        gateway.start();
        
        std::cout << "Gateway is running. Press Ctrl+C to stop." << std::endl;
        
        // 主循环
        while (g_running && gateway.is_running()) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        
        // 停止网关
        gateway.stop();
        
        Logger::info("=== Gateway Stopped ===");
        std::cout << "Gateway stopped successfully." << std::endl;
        
        return 0;
        
    } catch (const ConfigError& e) {
        std::cerr << "Configuration error: " << e.what() << std::endl;
        Logger::error("Configuration error: " + std::string(e.what()));
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        Logger::error("Fatal error: " + std::string(e.what()));
        return 1;
    }
}
