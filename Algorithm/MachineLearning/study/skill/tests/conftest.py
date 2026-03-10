"""Pytest 配置和 fixtures 模块。

本模块配置 pytest fixtures 和 hypothesis 设置，为属性测试和单元测试提供通用支持。
"""

import sys
from pathlib import Path
from typing import Callable, List

import pytest
from hypothesis import settings, Verbosity

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from skill import Skill
from registry import SkillRegistry
from dispatcher import SkillDispatcher
from demo_skill import create_greeting_skill


# ============================================================================
# Hypothesis 配置
# ============================================================================

# 配置 hypothesis 默认设置：最少 100 次迭代
settings.register_profile(
    "default",
    max_examples=100,
    verbosity=Verbosity.normal,
)

settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.verbose,
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.verbose,
)

# 加载默认配置
settings.load_profile("default")


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def empty_registry() -> SkillRegistry:
    """创建空的 SkillRegistry 实例。
    
    Returns:
        空的 SkillRegistry 实例
    """
    return SkillRegistry()


@pytest.fixture
def greeting_skill() -> Skill:
    """创建 greeting demo skill。
    
    Returns:
        greeting Skill 实例
    """
    return create_greeting_skill()


@pytest.fixture
def sample_skill() -> Skill:
    """创建一个简单的示例 skill 用于测试。
    
    Returns:
        示例 Skill 实例
    """
    return Skill(
        name="sample",
        description="示例 skill",
        keywords=["test", "sample", "示例"],
        handler=lambda: "这是示例响应"
    )


@pytest.fixture
def registry_with_greeting(empty_registry: SkillRegistry, greeting_skill: Skill) -> SkillRegistry:
    """创建包含 greeting skill 的 SkillRegistry。
    
    Args:
        empty_registry: 空的注册表
        greeting_skill: greeting skill 实例
        
    Returns:
        包含 greeting skill 的 SkillRegistry
    """
    empty_registry.register(greeting_skill)
    return empty_registry


@pytest.fixture
def registry_with_sample(empty_registry: SkillRegistry, sample_skill: Skill) -> SkillRegistry:
    """创建包含 sample skill 的 SkillRegistry。
    
    Args:
        empty_registry: 空的注册表
        sample_skill: sample skill 实例
        
    Returns:
        包含 sample skill 的 SkillRegistry
    """
    empty_registry.register(sample_skill)
    return empty_registry


@pytest.fixture
def dispatcher_with_greeting(registry_with_greeting: SkillRegistry) -> SkillDispatcher:
    """创建包含 greeting skill 的 SkillDispatcher。
    
    Args:
        registry_with_greeting: 包含 greeting skill 的注册表
        
    Returns:
        配置好的 SkillDispatcher 实例
    """
    return SkillDispatcher(registry_with_greeting)


@pytest.fixture
def empty_dispatcher(empty_registry: SkillRegistry) -> SkillDispatcher:
    """创建空的 SkillDispatcher（无注册 skill）。
    
    Args:
        empty_registry: 空的注册表
        
    Returns:
        空的 SkillDispatcher 实例
    """
    return SkillDispatcher(empty_registry)


# ============================================================================
# 测试辅助函数
# ============================================================================

def create_test_skill(
    name: str = "test_skill",
    description: str = "测试 skill",
    keywords: List[str] = None,
    handler: Callable[[], str] = None
) -> Skill:
    """创建测试用 Skill 实例的辅助函数。
    
    Args:
        name: skill 名称，默认为 "test_skill"
        description: skill 描述，默认为 "测试 skill"
        keywords: 关键词列表，默认为 ["test"]
        handler: 处理函数，默认返回 "test response"
        
    Returns:
        配置好的 Skill 实例
    """
    if keywords is None:
        keywords = ["test"]
    if handler is None:
        handler = lambda: "test response"
    
    return Skill(
        name=name,
        description=description,
        keywords=keywords,
        handler=handler
    )


def create_skill_with_error_handler(name: str = "error_skill") -> Skill:
    """创建一个 handler 会抛出异常的 Skill。
    
    Args:
        name: skill 名称
        
    Returns:
        handler 会抛出异常的 Skill 实例
    """
    def error_handler() -> str:
        raise RuntimeError("模拟的错误")
    
    return Skill(
        name=name,
        description="会抛出错误的 skill",
        keywords=["error", "错误"],
        handler=error_handler
    )


def create_multiple_skills(count: int = 3) -> List[Skill]:
    """创建多个不同的测试 Skill。
    
    Args:
        count: 要创建的 skill 数量
        
    Returns:
        Skill 实例列表
    """
    skills = []
    for i in range(count):
        skill = Skill(
            name=f"skill_{i}",
            description=f"测试 skill {i}",
            keywords=[f"keyword_{i}", f"关键词_{i}"],
            handler=lambda idx=i: f"skill_{idx} 的响应"
        )
        skills.append(skill)
    return skills
