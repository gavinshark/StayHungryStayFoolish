"""LLM Dispatcher 模块。

使用大模型来智能选择和调用 skill。
"""

import json
import os
from typing import Optional

from registry import SkillRegistry
from skill import Skill


class LLMDispatcher:
    """基于大模型的 Skill 调度器。
    
    使用 LLM 分析用户查询，智能选择最匹配的 skill。
    """
    
    def __init__(self, registry: SkillRegistry, api_key: str = None, base_url: str = None):
        """初始化 LLM dispatcher。
        
        Args:
            registry: SkillRegistry 实例
            api_key: OpenAI API key，默认从环境变量读取
            base_url: API base URL，支持自定义端点
        """
        self._registry = registry
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    def _build_skill_descriptions(self) -> str:
        """构建所有 skill 的描述信息供 LLM 参考。"""
        skills = self._registry.get_all_skills()
        if not skills:
            return "当前没有可用的 skill。"
        
        descriptions = []
        for skill in skills:
            desc = f"- {skill.name}: {skill.description} (关键词: {', '.join(skill.keywords)})"
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def _call_llm(self, user_query: str) -> Optional[str]:
        """调用 LLM 选择合适的 skill。
        
        Args:
            user_query: 用户查询
            
        Returns:
            选中的 skill 名称，如果无匹配返回 None
        """
        try:
            import httpx
        except ImportError:
            print("请安装 httpx: pip install httpx")
            return None
        
        if not self._api_key:
            print("未设置 OPENAI_API_KEY 环境变量")
            return None
        
        skill_descriptions = self._build_skill_descriptions()
        skill_names = [s.name for s in self._registry.get_all_skills()]
        
        system_prompt = f"""你是一个 skill 选择器。根据用户的输入，选择最合适的 skill 来处理。

可用的 skills:
{skill_descriptions}

请只返回一个 JSON 对象，格式如下：
{{"skill": "skill名称"}} 或 {{"skill": null}} 如果没有合适的 skill

不要返回任何其他内容。"""

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": os.getenv("OPENAI_MODEL", "qwen-turbo"),
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_query}
                        ],
                        "temperature": 0
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # 解析 JSON 响应
                parsed = json.loads(content)
                selected = parsed.get("skill")
                
                if selected and selected in skill_names:
                    return selected
                return None
                
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return None
    
    def dispatch(self, query: str) -> str:
        """使用 LLM 分析查询并调用匹配的 skill。
        
        Args:
            query: 用户输入的查询字符串
            
        Returns:
            skill 执行结果或提示信息
        """
        if not query or not query.strip():
            return "未找到匹配的 skill"
        
        # 调用 LLM 选择 skill
        selected_skill_name = self._call_llm(query)
        
        if not selected_skill_name:
            return "未找到匹配的 skill"
        
        # 查找并执行 skill
        skill = self._registry.find_by_name(selected_skill_name)
        if not skill:
            return "未找到匹配的 skill"
        
        try:
            return skill.handler()
        except Exception as e:
            return f"执行 skill '{skill.name}' 时发生错误: {str(e)}"
