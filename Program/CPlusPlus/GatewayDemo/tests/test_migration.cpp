// 测试技术栈迁移是否成功
#include <iostream>
#include <cassert>

// 测试spdlog
#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>

// 测试nlohmann/json
#include <nlohmann/json.hpp>

// 测试Asio (可选，如果已安装)
#ifdef HAS_ASIO
#include <asio.hpp>
#endif

using json = nlohmann::json;

void test_spdlog() {
    std::cout << "Testing spdlog..." << std::endl;
    
    try {
        auto console = spdlog::stdout_color_mt("test_console");
        console->info("spdlog test: {}", "OK");
        console->warn("Warning level: {}", 1);
        console->error("Error level: {}", 2);
        
        spdlog::drop("test_console");
        std::cout << "✅ spdlog test passed" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "❌ spdlog test failed: " << e.what() << std::endl;
        throw;
    }
}

void test_nlohmann_json() {
    std::cout << "\nTesting nlohmann/json..." << std::endl;
    
    try {
        // 创建JSON对象
        json j = {
            {"name", "gateway"},
            {"version", "2.0.0"},
            {"port", 8080},
            {"features", {"routing", "load_balancing", "logging"}}
        };
        
        // 序列化
        std::string json_str = j.dump(2);
        std::cout << "JSON output:\n" << json_str << std::endl;
        
        // 解析
        json parsed = json::parse(json_str);
        assert(parsed["name"] == "gateway");
        assert(parsed["port"] == 8080);
        assert(parsed["features"].size() == 3);
        
        // 测试默认值
        int timeout = parsed.value("timeout", 5000);
        assert(timeout == 5000);
        
        std::cout << "✅ nlohmann/json test passed" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "❌ nlohmann/json test failed: " << e.what() << std::endl;
        throw;
    }
}

void test_asio() {
#ifdef HAS_ASIO
    std::cout << "\nTesting Asio..." << std::endl;
    
    try {
        asio::io_context io_context;
        
        // 测试定时器
        asio::steady_timer timer(io_context, std::chrono::milliseconds(100));
        bool timer_fired = false;
        
        timer.async_wait([&timer_fired](const std::error_code& ec) {
            if (!ec) {
                timer_fired = true;
            }
        });
        
        io_context.run();
        assert(timer_fired);
        
        std::cout << "✅ Asio test passed" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "❌ Asio test failed: " << e.what() << std::endl;
        throw;
    }
#else
    std::cout << "\n⏭️  Asio test skipped (not installed yet)" << std::endl;
#endif
}

void test_config_parsing() {
    std::cout << "\nTesting config parsing..." << std::endl;
    
    try {
        // 模拟配置文件内容
        std::string config_str = R"({
            "listen_port": 8080,
            "log_level": "info",
            "log_file": "log/gateway.log",
            "backend_timeout_ms": 5000,
            "client_timeout_ms": 30000,
            "routes": [
                {
                    "path_pattern": "/api",
                    "match_type": "prefix",
                    "priority": 1,
                    "backends": ["http://localhost:9001", "http://localhost:9002"]
                }
            ]
        })";
        
        json config = json::parse(config_str);
        
        // 验证解析结果
        assert(config["listen_port"] == 8080);
        assert(config["log_level"] == "info");
        assert(config["routes"].is_array());
        assert(config["routes"].size() == 1);
        assert(config["routes"][0]["backends"].size() == 2);
        
        std::cout << "✅ Config parsing test passed" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "❌ Config parsing test failed: " << e.what() << std::endl;
        throw;
    }
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "技术栈迁移测试" << std::endl;
    std::cout << "========================================" << std::endl;
    
    try {
        test_spdlog();
        test_nlohmann_json();
        test_config_parsing();
        test_asio();
        
        std::cout << "\n========================================" << std::endl;
        std::cout << "✅ 所有测试通过！" << std::endl;
        std::cout << "========================================" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cout << "\n========================================" << std::endl;
        std::cout << "❌ 测试失败: " << e.what() << std::endl;
        std::cout << "========================================" << std::endl;
        return 1;
    }
}
