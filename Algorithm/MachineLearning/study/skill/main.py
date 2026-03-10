"""主程序入口模块。

本模块实现命令行交互界面，动态加载 skills 并使用 LLM 进行智能调度。
"""

import os
from pathlib import Path

from registry import SkillRegistry
from dispatcher import SkillDispatcher
from llm_dispatcher import LLMDispatcher
from demo_skill import load_skills_from_directory


def display_welcome(skills_count: int, use_llm: bool) -> None:
    """显示欢迎信息和使用说明。"""
    print("=" * 50)
    print("欢迎使用 Python Skill Demo 程序！")
    print("=" * 50)
    print()
    print(f"已加载 {skills_count} 个 skills")
    print(f"调度模式: {'LLM 智能调度' if use_llm else '关键词匹配'}")
    print()
    print("使用说明：")
    print("  - 输入您的问题或指令，系统将调用匹配的 skill")
    print("  - 输入 'list' 查看所有可用 skills")
    print("  - 输入 'exit' 或 'quit' 退出程序")
    print()


def list_skills(registry: SkillRegistry) -> None:
    """列出所有已加载的 skills。"""
    skills = registry.get_all_skills()
    if not skills:
        print("当前没有加载任何 skill")
        return
    
    print(f"\n已加载的 skills ({len(skills)} 个):")
    for skill in skills:
        print(f"  - {skill.name}")
        print(f"    描述: {skill.description}")
        print(f"    关键词: {', '.join(skill.keywords)}")
    print()


def main() -> None:
    """主程序入口函数。"""
    # 初始化 SkillRegistry
    registry = SkillRegistry()
    
    # 动态加载 .kiro/skills/ 下所有 skills
    skills_dir = Path(".kiro/skills")
    skills = load_skills_from_directory(skills_dir)
    
    for skill in skills:
        registry.register(skill)
    
    # 检查是否配置了 LLM
    use_llm = bool(os.getenv("OPENAI_API_KEY"))
    
    # 根据配置选择调度器
    if use_llm:
        dispatcher = LLMDispatcher(registry)
    else:
        dispatcher = SkillDispatcher(registry)
    
    # 显示欢迎信息
    display_welcome(len(skills), use_llm)
    
    # 用户输入循环
    while True:
        try:
            user_input = input("请输入您的问题 > ").strip()
            
            # 处理退出命令
            if user_input.lower() in ("exit", "quit"):
                print("感谢使用，再见！")
                break
            
            # 处理列表命令
            if user_input.lower() == "list":
                list_skills(registry)
                continue
            
            # 调度查询并显示结果
            result = dispatcher.dispatch(user_input)
            print(f"\n{result}\n")
            
        except EOFError:
            print("\n感谢使用，再见！")
            break
        except KeyboardInterrupt:
            print("\n感谢使用，再见！")
            break


if __name__ == "__main__":
    main()
