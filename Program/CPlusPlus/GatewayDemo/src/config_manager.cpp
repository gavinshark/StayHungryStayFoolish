#include "config_manager.hpp"
#include <fstream>
#include <algorithm>

namespace gateway {

GatewayConfig ConfigManager::load_from_file(const std::string& config_path) {
    std::ifstream file(config_path);
    if (!file.is_open()) {
        throw ConfigError("Cannot open config file: " + config_path);
    }

    try {
        json j = json::parse(file);
        GatewayConfig config = parse_json(j);
        validate_config(config);
        return config;
    } catch (const json::parse_error& e) {
        throw ConfigError(std::string("JSON parse error: ") + e.what());
    } catch (const json::type_error& e) {
        throw ConfigError(std::string("JSON type error: ") + e.what());
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

GatewayConfig ConfigManager::parse_json(const json& j) {
    GatewayConfig config;
    
    // 解析基本字段（使用默认值）
    config.listen_port = j.value("listen_port", 8080);
    config.log_level = j.value("log_level", "info");
    config.log_file = j.value("log_file", "log/gateway.log");
    config.backend_timeout_ms = j.value("backend_timeout_ms", 5000);
    config.client_timeout_ms = j.value("client_timeout_ms", 30000);
    
    // 解析路由数组
    if (j.contains("routes") && j["routes"].is_array()) {
        for (const auto& route_json : j["routes"]) {
            Route route;
            
            // 必需字段
            if (!route_json.contains("path_pattern")) {
                throw ConfigError("Route missing required field: path_pattern");
            }
            route.path_pattern = route_json["path_pattern"];
            
            // 匹配类型（默认为prefix）
            std::string match_type_str = route_json.value("match_type", "prefix");
            route.match_type = parse_match_type(match_type_str);
            
            // 优先级（默认为1）
            route.priority = route_json.value("priority", 1);
            
            // 后端列表
            if (!route_json.contains("backends") || !route_json["backends"].is_array()) {
                throw ConfigError("Route missing required field: backends (array)");
            }
            
            for (const auto& backend : route_json["backends"]) {
                if (backend.is_string()) {
                    route.backends.push_back(backend.get<std::string>());
                }
            }
            
            if (route.backends.empty()) {
                throw ConfigError("Route must have at least one backend");
            }
            
            config.routes.push_back(route);
        }
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
