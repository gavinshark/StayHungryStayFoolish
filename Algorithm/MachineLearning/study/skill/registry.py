"""SkillRegistry 模块。

本模块实现 SkillRegistry 类，用于管理和存储所有已注册的 skill。
"""

from typing import Dict, List, Optional

from skill import Skill


class SkillRegistry:
    """Skill 注册表，管理所有已注册的 skill。
    
    使用 Dict[str, Skill] 存储已注册的 skill，以 name 为键实现 O(1) 查找和覆盖。
    """
    
    def __init__(self) -> None:
        """初始化空的 skill 注册表。"""
        self._skills: Dict[str, Skill] = {}
    
    def register(self, skill: Skill) -> None:
        """注册 skill，如果名称已存在则覆盖。
        
        Args:
            skill: 要注册的 Skill 实例
        """
        self._skills[skill.name] = skill
    
    def get_all_skills(self) -> List[Skill]:
        """获取所有已注册的 skill 列表。
        
        Returns:
            包含所有已注册 skill 的列表
        """
        return list(self._skills.values())
    
    def find_by_name(self, name: str) -> Optional[Skill]:
        """根据名称查找 skill。
        
        Args:
            name: 要查找的 skill 名称
            
        Returns:
            找到的 Skill 实例，如果不存在则返回 None
        """
        return self._skills.get(name)
