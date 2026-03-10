"""Skill 数据类定义模块。

本模块定义了 Skill 数据类，用于表示一个可执行的功能单元。
"""

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Skill:
    """Skill 数据类，表示一个可执行的功能单元。
    
    Attributes:
        name: 唯一标识名称
        description: 功能描述
        keywords: 匹配关键词列表
        handler: 处理函数，返回字符串结果
    """
    name: str
    description: str
    keywords: List[str]
    handler: Callable[[], str]
