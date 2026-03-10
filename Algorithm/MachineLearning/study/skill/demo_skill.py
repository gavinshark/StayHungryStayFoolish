"""Demo Skill 实现模块。

本模块提供从 .kiro/skills/ 目录加载 skill 的功能。
每个 skill 是一个文件夹，包含：
- {name}.md: skill 描述文件
- {name}.py: skill 执行脚本（需包含 run() 函数）
"""

import importlib.util
from pathlib import Path
from typing import Callable, List, Optional

from skill import Skill


def parse_skill_markdown(content: str) -> dict:
    """解析 skill markdown 文件内容。
    
    Args:
        content: markdown 文件内容
        
    Returns:
        包含 name, description, keywords, script 的字典
    """
    result = {
        "name": "",
        "description": "",
        "keywords": [],
        "script": ""
    }
    
    lines = content.strip().split("\n")
    current_section = None
    
    for line in lines:
        if line.startswith("# "):
            result["name"] = line[2:].strip().lower().replace(" ", "-")
            continue
        
        if result["name"] and not result["description"] and line.strip() and not line.startswith("#"):
            result["description"] = line.strip()
            continue
        
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            continue
        
        if current_section == "触发关键词" and line.startswith("- "):
            result["keywords"].append(line[2:].strip())
            continue
        
        if current_section == "执行脚本" and line.strip().endswith(".py"):
            result["script"] = line.strip()
            continue
    
    return result


def load_script_handler(script_path: Path) -> Optional[Callable[[], str]]:
    """从 Python 脚本加载 run() 函数作为 handler。
    
    Args:
        script_path: 脚本文件路径
        
    Returns:
        run 函数，如果加载失败返回 None
    """
    if not script_path.exists():
        return None
    
    spec = importlib.util.spec_from_file_location("skill_script", script_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if hasattr(module, "run") and callable(module.run):
        return module.run
    
    return None


def load_skill_from_directory(skill_dir: Path) -> Optional[Skill]:
    """从 skill 目录加载 skill。
    
    Args:
        skill_dir: skill 目录路径
        
    Returns:
        Skill 实例，如果加载失败返回 None
    """
    md_files = list(skill_dir.glob("*.md"))
    if not md_files:
        return None
    
    md_file = md_files[0]
    content = md_file.read_text(encoding="utf-8")
    parsed = parse_skill_markdown(content)
    
    if not parsed["name"] or not parsed["keywords"]:
        return None
    
    # 加载执行脚本
    script_name = parsed["script"] or f"{skill_dir.name}.py"
    script_path = skill_dir / script_name
    handler = load_script_handler(script_path)
    
    if handler is None:
        handler = lambda: f"[{parsed['name']}] 脚本未找到或无 run() 函数"
    
    return Skill(
        name=parsed["name"],
        description=parsed["description"],
        keywords=parsed["keywords"],
        handler=handler
    )


def load_skills_from_directory(skills_dir: Path = None) -> List[Skill]:
    """从 .kiro/skills/ 目录加载所有 skill。
    
    Args:
        skills_dir: skills 目录路径，默认为 .kiro/skills/
        
    Returns:
        加载的 Skill 列表
    """
    if skills_dir is None:
        skills_dir = Path(".kiro/skills")
    
    if not skills_dir.exists():
        return []
    
    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir():
            skill = load_skill_from_directory(item)
            if skill:
                skills.append(skill)
    
    return skills


def create_greeting_skill() -> Skill:
    """创建 greeting demo skill。
    
    优先从 .kiro/skills/greeting/ 加载，
    如果目录不存在则使用默认配置。
    
    Returns:
        Skill: 配置好的 greeting skill 实例
    """
    skill_dir = Path(".kiro/skills/greeting")
    
    if skill_dir.exists():
        skill = load_skill_from_directory(skill_dir)
        if skill:
            return skill
    
    # 默认配置（fallback）
    return Skill(
        name="greeting",
        description="问候 skill，响应用户的打招呼请求",
        keywords=["你好", "hello", "hi"],
        handler=lambda: "你好！很高兴见到你！有什么我可以帮助你的吗？"
    )
