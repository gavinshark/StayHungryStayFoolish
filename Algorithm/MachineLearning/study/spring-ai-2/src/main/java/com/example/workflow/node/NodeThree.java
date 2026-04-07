package com.example.workflow.node;

import com.example.workflow.exception.WorkflowException;
import com.example.workflow.model.WorkflowContext;
import com.example.workflow.service.ChatService;
import org.springframework.stereotype.Component;

/**
 * 工作流第三个节点 - 最终处理节点
 * 接收 NodeTwo 的输出并通过 ChatService 调用大模型进行最终总结处理
 */
@Component
public class NodeThree implements WorkflowNode {
    
    private final ChatService chatService;
    
    public NodeThree(ChatService chatService) {
        this.chatService = chatService;
    }
    
    @Override
    public WorkflowContext process(WorkflowContext context) throws WorkflowException {
        String input = context.getNodeTwoOutput();
        String prompt = buildPrompt(input);
        String result = chatService.chat(prompt);
        context.setFinalOutput(result);
        return context;
    }
    
    @Override
    public String getName() {
        return "NodeThree";
    }
    
    /**
     * 构建最终处理的提示词
     * @param input NodeTwo 的输出
     * @return 完整的提示词
     */
    private String buildPrompt(String input) {
        return "请对以下内容进行最终总结：" + input;
    }
}
