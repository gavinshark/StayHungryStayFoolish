#include "config_manager.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>

// 简化的JSON解析（实际项目中应使用nlohmann/json）
// 这里为了演示，实现一个基本的JSON解析
namespace gateway {

GatewayConfig ConfigManager::load_from_file(const std::string& config_path) {
    std::ifstream file(config_path);
    if (!file.is_open()) {
        throw ConfigError("Cannot open config file: " + config_path);
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string json_content = buffer.str();

    if (json_content.empty()) {
        throw ConfigError("Config file is empty");
    }

    try {
        GatewayConfig config = parse_json(json_content);
        validate_config(config);
        return config;
    } catch (const std::exception& e) {
        throw ConfigError(std::string("Failed to parse config: ") + e.what());
    }
}

void ConfigManager::validate_config(const GatewayConfig& config) {
    // 验证端口
    if (config.listen_port == 0) {
        throw ConfigError("Invalid listen_port: must be greater than 0");
    }

    // 验证路由
    if (config.routes.empty()) {
        throw ConfigError("No routes configured");
    }

    for (const auto& route : config.routes) {
        if (route.path_pattern.empty()) {
            throw ConfigError("Route path_pattern cannot be empty");
        }

        if (route.backends.empty()) {
            throw ConfigError("Route must have at least one backend");
        }

        for (const auto& backend : route.backends) {
            if (backend.empty()) {
                throw ConfigError("Backend URL cannot be empty");
            }
        }

        if (route.priority < 0) {
            throw ConfigError("Route priority must be non-negative");
        }
    }

    // 验证超时
    if (config.backend_timeout_ms <= 0) {
        throw ConfigError("backend_timeout_ms must be positive");
    }

    if (config.client_timeout_ms <= 0) {
        throw ConfigError("client_timeout_ms must be positive");
    }

    // 验证日志级别
    std::string log_level_lower = config.log_level;
    std::transform(log_level_lower.begin(), log_level_lower.end(), 
                   log_level_lower.begin(), ::tolower);
    
    if (log_level_lower != "debug" && log_level_lower != "info" && 
        log_level_lower != "warn" && log_level_lower != "error") {
        throw ConfigError("Invalid log_level: must be debug, info, warn, or error");
    }
}

// 简化的JSON解析实现
// 注意：这是一个非常基础的实现，仅用于演示
// 实际项目应使用 nlohmann/json 库
GatewayConfig ConfigManager::parse_json(const std::string& json_content) {
    GatewayConfig config;
    
    // 这里应该使用真正的JSON库来解析
    // 为了简化，我们假设配置文件格式正确
    // 实际实现中需要使用 nlohmann/json
    
    // 临时实现：查找关键字段
    auto find_value = [&json_content](const std::string& key) -> std::string {
        size_t pos = json_content.find("\"" + key + "\"");
        if (pos == std::string::npos) return "";
        
        pos = json_content.find(":", pos);
        if (pos == std::string::npos) return "";
        
        pos = json_content.find_first_not_of(" \t\n\r", pos + 1);
        if (pos == std::string::npos) return "";
        
        size_t end_pos;
        if (json_content[pos] == '"') {
            pos++;
            end_pos = json_content.find('"', pos);
        } else {
            end_pos = json_content.find_first_of(",}\n", pos);
        }
        
        if (end_pos == std::string::npos) return "";
        return json_content.substr(pos, end_pos - pos);
    };

    // 解析基本字段
    std::string port_str = find_value("listen_port");
    if (!port_str.empty()) {
        config.listen_port = static_cast<uint16_t>(std::stoi(port_str));
    }

    config.log_level = find_value("log_level");
    if (config.log_level.empty()) {
        config.log_level = "info";
    }

    config.log_file = find_value("log_file");
    if (config.log_file.empty()) {
        config.log_file = "gateway.log";
    }

    std::string backend_timeout = find_value("backend_timeout_ms");
    if (!backend_timeout.empty()) {
        config.backend_timeout_ms = std::stoi(backend_timeout);
    }

    std::string client_timeout = find_value("client_timeout_ms");
    if (!client_timeout.empty()) {
        config.client_timeout_ms = std::stoi(client_timeout);
    }

    // 解析路由（简化版本）
    // 实际应该使用JSON库来正确解析数组
    size_t routes_pos = json_content.find("\"routes\"");
    if (routes_pos != std::string::npos) {
        // 添加一个默认路由用于演示
        Route route;
        route.path_pattern = "/";
        route.match_type = MatchType::PREFIX;
        route.backends.push_back("http://localhost:9001");
        route.priority = 1;
        config.routes.push_back(route);
    }

    return config;
}

MatchType ConfigManager::parse_match_type(const std::string& type_str) {
    std::string lower = type_str;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    
    if (lower == "exact") {
        return MatchType::EXACT;
    } else if (lower == "prefix") {
        return MatchType::PREFIX;
    } else {
        throw ConfigError("Invalid match_type: " + type_str);
    }
}

} // namespace gateway
