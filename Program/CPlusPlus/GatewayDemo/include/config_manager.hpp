#pragma once

#include "config_types.hpp"
#include <string>
#include <stdexcept>

namespace gateway {

class ConfigError : public std::runtime_error {
public:
    explicit ConfigError(const std::string& message)
        : std::runtime_error(message) {}
};

class ConfigManager {
public:
    // 从文件加载配置
    static GatewayConfig load_from_file(const std::string& config_path);
    
    // 验证配置
    static void validate_config(const GatewayConfig& config);

private:
    // 解析JSON配置
    static GatewayConfig parse_json(const std::string& json_content);
    
    // 解析匹配类型
    static MatchType parse_match_type(const std::string& type_str);
};

} // namespace gateway
