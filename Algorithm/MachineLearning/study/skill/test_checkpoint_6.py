"""检查点 6 测试 - 验证调度和 Demo Skill 功能。

本测试文件验证：
1. dispatcher.py 可以导入且 SkillDispatcher 类正常工作
2. demo_skill.py 可以导入且 create_greeting_skill() 正常工作
3. 集成测试：创建 greeting skill，注册它，使用关键词 "你好"、"hello"、"hi" 调度查询并验证正确响应
4. 验证无匹配情况返回 "未找到匹配的 skill"
"""

import pytest


class TestCheckpoint6:
    """检查点 6 测试类。"""
    
    def test_dispatcher_import(self):
        """测试 dispatcher.py 可以导入且 SkillDispatcher 类存在。"""
        from dispatcher import SkillDispatcher
        assert SkillDispatcher is not None
    
    def test_demo_skill_import(self):
        """测试 demo_skill.py 可以导入且 create_greeting_skill 函数存在。"""
        from demo_skill import create_greeting_skill
        assert create_greeting_skill is not None
    
    def test_create_greeting_skill_works(self):
        """测试 create_greeting_skill() 返回正确配置的 skill。"""
        from demo_skill import create_greeting_skill
        
        skill = create_greeting_skill()
        
        assert skill.name == "greeting"
        assert "你好" in skill.keywords
        assert "hello" in skill.keywords
        assert "hi" in skill.keywords
        assert callable(skill.handler)
        
        # 验证 handler 返回字符串
        result = skill.handler()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_integration_dispatch_chinese_keyword(self):
        """集成测试：使用中文关键词 "你好" 调度查询。"""
        from registry import SkillRegistry
        from dispatcher import SkillDispatcher
        from demo_skill import create_greeting_skill
        
        # 创建并注册 greeting skill
        registry = SkillRegistry()
        skill = create_greeting_skill()
        registry.register(skill)
        
        # 创建 dispatcher
        dispatcher = SkillDispatcher(registry)
        
        # 使用 "你好" 关键词调度
        result = dispatcher.dispatch("你好")
        
        # 验证返回 handler 的执行结果
        expected = skill.handler()
        assert result == expected
    
    def test_integration_dispatch_hello_keyword(self):
        """集成测试：使用英文关键词 "hello" 调度查询。"""
        from registry import SkillRegistry
        from dispatcher import SkillDispatcher
        from demo_skill import create_greeting_skill
        
        registry = SkillRegistry()
        skill = create_greeting_skill()
        registry.register(skill)
        dispatcher = SkillDispatcher(registry)
        
        result = dispatcher.dispatch("hello there!")
        expected = skill.handler()
        assert result == expected
    
    def test_integration_dispatch_hi_keyword(self):
        """集成测试：使用英文关键词 "hi" 调度查询。"""
        from registry import SkillRegistry
        from dispatcher import SkillDispatcher
        from demo_skill import create_greeting_skill
        
        registry = SkillRegistry()
        skill = create_greeting_skill()
        registry.register(skill)
        dispatcher = SkillDispatcher(registry)
        
        result = dispatcher.dispatch("hi, how are you?")
        expected = skill.handler()
        assert result == expected
    
    def test_integration_dispatch_case_insensitive(self):
        """集成测试：验证关键词匹配忽略大小写。"""
        from registry import SkillRegistry
        from dispatcher import SkillDispatcher
        from demo_skill import create_greeting_skill
        
        registry = SkillRegistry()
        skill = create_greeting_skill()
        registry.register(skill)
        dispatcher = SkillDispatcher(registry)
        
        # 测试大写 HELLO
        result = dispatcher.dispatch("HELLO")
        expected = skill.handler()
        assert result == expected
        
        # 测试混合大小写 HeLLo
        result = dispatcher.dispatch("HeLLo World")
        assert result == expected
    
    def test_integration_no_match_returns_prompt(self):
        """集成测试：验证无匹配情况返回 "未找到匹配的 skill"。"""
        from registry import SkillRegistry
        from dispatcher import SkillDispatcher
        from demo_skill import create_greeting_skill
        
        registry = SkillRegistry()
        skill = create_greeting_skill()
        registry.register(skill)
        dispatcher = SkillDispatcher(registry)
        
        # 使用不包含任何关键词的查询
        result = dispatcher.dispatch("今天天气怎么样？")
        assert result == "未找到匹配的 skill"
        
        # 测试另一个不匹配的查询
        result = dispatcher.dispatch("what is the weather?")
        assert result == "未找到匹配的 skill"
    
    def test_integration_empty_query_returns_prompt(self):
        """集成测试：验证空查询返回 "未找到匹配的 skill"。"""
        from registry import SkillRegistry
        from dispatcher import SkillDispatcher
        from demo_skill import create_greeting_skill
        
        registry = SkillRegistry()
        skill = create_greeting_skill()
        registry.register(skill)
        dispatcher = SkillDispatcher(registry)
        
        # 空字符串
        result = dispatcher.dispatch("")
        assert result == "未找到匹配的 skill"
        
        # 纯空白
        result = dispatcher.dispatch("   ")
        assert result == "未找到匹配的 skill"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
