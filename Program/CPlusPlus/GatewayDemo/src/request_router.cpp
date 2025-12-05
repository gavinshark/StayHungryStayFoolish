#include "request_router.hpp"

namespace gateway {

void RequestRouter::add_route(const Route& route) {
    routes_.push_back(route);
    
    // 按优先级排序（优先级数值越小越靠前）
    std::sort(routes_.begin(), routes_.end(), 
              [](const Route& a, const Route& b) {
                  return a.priority < b.priority;
              });
}

std::optional<Route> RequestRouter::match_route(const std::string& path) const {
    // 按优先级顺序查找匹配的路由
    for (const auto& route : routes_) {
        if (is_match(path, route)) {
            return route;
        }
    }
    
    // 没有匹配的路由
    return std::nullopt;
}

void RequestRouter::clear_routes() {
    routes_.clear();
}

bool RequestRouter::is_match(const std::string& path, const Route& route) const {
    switch (route.match_type) {
        case MatchType::EXACT:
            // 精确匹配
            return path == route.path_pattern;
            
        case MatchType::PREFIX:
            // 前缀匹配
            if (path.length() < route.path_pattern.length()) {
                return false;
            }
            return path.compare(0, route.path_pattern.length(), route.path_pattern) == 0;
            
        default:
            return false;
    }
}

} // namespace gateway
