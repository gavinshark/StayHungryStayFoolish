"""SkillDispatcher 模块。

本模块实现 SkillDispatcher 类，用于解析用户查询并调用匹配的 skill。
"""

from registry import SkillRegistry


class SkillDispatcher:
    """Skill 调度器，根据用户输入匹配并调用相应的 skill。
    
    采用简单的子字符串匹配逻辑：
    1. 将用户查询转换为小写
    2. 遍历所有已注册 skill 的 keywords
    3. 检查任一 keyword 是否为查询的子字符串
    4. 返回第一个匹配的 skill 结果
    """
    
    def __init__(self, registry: SkillRegistry) -> None:
        """初始化 dispatcher，关联 skill 注册表。
        
        Args:
            registry: SkillRegistry 实例，用于获取已注册的 skill
        """
        self._registry = registry
    
    def dispatch(self, query: str) -> str:
        """解析用户查询并调用匹配的 skill。
        
        Args:
            query: 用户输入的查询字符串
            
        Returns:
            skill 执行结果或 "未找到匹配的 skill" 提示
        """
        # 处理空查询或纯空白查询
        if not query or not query.strip():
            return "未找到匹配的 skill"
        
        # 将查询转换为小写进行匹配
        query_lower = query.lower()
        
        # 遍历所有已注册的 skill
        for skill in self._registry.get_all_skills():
            # 检查任一 keyword 是否为查询的子字符串
            for keyword in skill.keywords:
                if keyword.lower() in query_lower:
                    # 找到匹配，调用 handler 并返回结果
                    try:
                        return skill.handler()
                    except Exception as e:
                        return f"执行 skill '{skill.name}' 时发生错误: {str(e)}"
        
        # 未找到匹配的 skill
        return "未找到匹配的 skill"
