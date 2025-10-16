# attractions_sse.py
from fastmcp import FastMCP

# 创建MCP服务器实例，指定端口
mcp = FastMCP("Attractions Service", port=8080)

# 模拟的旅游景点数据
attractions_data = {
    "New York": [
        {"name": "Statue of Liberty", "category": "landmark", "highlight": "Iconic statue on Liberty Island"},
        {"name": "Central Park", "category": "park", "highlight": "Urban oasis with lakes and trails"},
        {"name": "Metropolitan Museum of Art", "category": "museum", "highlight": "World-class art collection"}
    ],
    "London": [
        {"name": "Tower of London", "category": "castle", "highlight": "Historic fortress and Crown Jewels"},
        {"name": "British Museum", "category": "museum", "highlight": "Artifacts from around the world"},
        {"name": "London Eye", "category": "observation", "highlight": "Riverside giant Ferris wheel"}
    ],
    "Tokyo": [
        {"name": "Senso-ji", "category": "temple", "highlight": "Historic Buddhist temple in Asakusa"},
        {"name": "Shibuya Crossing", "category": "landmark", "highlight": "One of the busiest crossings"},
        {"name": "Meiji Shrine", "category": "shrine", "highlight": "Shinto shrine in a forested area"}
    ],
    "Sydney": [
        {"name": "Sydney Opera House", "category": "landmark", "highlight": "Sail-like iconic architecture"},
        {"name": "Harbour Bridge", "category": "bridge", "highlight": "Climb for panoramic harbour views"},
        {"name": "Bondi Beach", "category": "beach", "highlight": "Famous surf beach and coastal walk"}
    ]
}

@mcp.tool()
def get_attractions(city: str) -> dict:
    """获取指定城市的旅游景点列表"""
    if city not in attractions_data:
        return {"error": f"无法找到城市 {city} 的景点数据"}
    return {"city": city, "attractions": attractions_data[city]}

@mcp.resource("attractions://cities")
def get_available_cities() -> list:
    """获取所有可用城市列表"""
    return list(attractions_data.keys())

@mcp.resource("attractions://list/{city}")
def get_city_attractions(city: str) -> dict:
    """获取指定城市的旅游景点资源列表"""
    if city not in attractions_data:
        return {"error": f"无法找到城市 {city} 的景点数据"}
    return {"city": city, "attractions": attractions_data[city]}

if __name__ == "__main__":
    # 使用SSE传输方式启动服务器
    mcp.run(transport="sse")