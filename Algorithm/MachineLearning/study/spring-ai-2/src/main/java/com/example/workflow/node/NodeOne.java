package com.example.workflow.node;

import com.example.workflow.exception.WorkflowException;
import com.example.workflow.model.WorkflowContext;
import com.example.workflow.service.ChatService;
import org.springframework.stereotype.Component;

/**
 * 工作流第一个节点 - 初始处理节点
 * 接收输入数据并通过 ChatService 调用大模型进行初始处理
 */
@Component
public class NodeOne implements WorkflowNode {
    
    private final ChatService chatService;
    
    public NodeOne(ChatService chatService) {
        this.chatService = chatService;
    }
    
    @Override
    public WorkflowContext process(WorkflowContext context) throws WorkflowException {
        String input = context.getInput();
        String prompt = buildPrompt(input);
        String result = chatService.chat(prompt);
        context.setNodeOneOutput(result);
        return context;
    }
    
    @Override
    public String getName() {
        return "NodeOne";
    }
    
    /**
     * 构建初始处理的提示词
     * @param input 用户输入
     * @return 完整的提示词
     */
    private String buildPrompt(String input) {
        return "请对以下内容进行初步分析：" + input;
    }
}
