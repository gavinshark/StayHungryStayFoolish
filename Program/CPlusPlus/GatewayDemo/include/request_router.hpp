#pragma once

#include "config_types.hpp"
#include <vector>
#include <optional>
#include <algorithm>

namespace gateway {

class RequestRouter {
public:
    RequestRouter() = default;
    
    // 添加路由规则
    void add_route(const Route& route);
    
    // 匹配路由
    std::optional<Route> match_route(const std::string& path) const;
    
    // 清除所有路由
    void clear_routes();
    
    // 获取所有路由
    const std::vector<Route>& get_routes() const { return routes_; }

private:
    // 检查路径是否匹配路由规则
    bool is_match(const std::string& path, const Route& route) const;
    
    std::vector<Route> routes_;  // 按优先级排序的路由列表
};

} // namespace gateway
