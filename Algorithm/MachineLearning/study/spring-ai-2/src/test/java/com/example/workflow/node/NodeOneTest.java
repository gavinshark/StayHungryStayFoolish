package com.example.workflow.node;

import com.example.workflow.model.WorkflowContext;
import com.example.workflow.service.ChatService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

/**
 * NodeOne 集成测试 - 直接调用真实大模型
 */
@SpringBootTest
class NodeOneTest {

    @Autowired
    private ChatService chatService;

    @Autowired
    private NodeOne nodeOne;

    @Test
    void process_shouldCallRealModelAndStoreResult() {
        String userInput = "Spring AI 是什么？请用一句话回答。";
        WorkflowContext context = new WorkflowContext(userInput);

        WorkflowContext result = nodeOne.process(context);

        assertSame(context, result);
        assertNotNull(result.getNodeOneOutput());
        assertFalse(result.getNodeOneOutput().isBlank());
        System.out.println("NodeOne output: " + result.getNodeOneOutput());
    }

    @Test
    void getName_shouldReturnNodeOne() {
        assertEquals("NodeOne", nodeOne.getName());
    }
}
