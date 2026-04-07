package com.example.workflow.node;

import com.example.workflow.exception.WorkflowException;
import com.example.workflow.model.WorkflowContext;
import com.example.workflow.service.ChatService;
import org.springframework.stereotype.Component;

/**
 * 工作流第二个节点 - 中间处理节点
 * 接收 NodeOne 的输出并通过 ChatService 调用大模型进行中间处理
 */
@Component
public class NodeTwo implements WorkflowNode {
    
    private final ChatService chatService;
    
    public NodeTwo(ChatService chatService) {
        this.chatService = chatService;
    }
    
    @Override
    public WorkflowContext process(WorkflowContext context) throws WorkflowException {
        String input = context.getNodeOneOutput();
        String prompt = buildPrompt(input);
        String result = chatService.chat(prompt);
        context.setNodeTwoOutput(result);
        return context;
    }
    
    @Override
    public String getName() {
        return "NodeTwo";
    }
    
    /**
     * 构建中间处理的提示词
     * @param input NodeOne 的输出
     * @return 完整的提示词
     */
    private String buildPrompt(String input) {
        return "请对以下分析结果进行深入处理：" + input;
    }
}
