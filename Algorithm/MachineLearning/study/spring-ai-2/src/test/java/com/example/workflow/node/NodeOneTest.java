package com.example.workflow.node;

import com.example.workflow.model.WorkflowContext;
import com.example.workflow.service.ChatService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * NodeOne 单元测试
 * Validates: Requirements 5.1, 5.2, 5.3, 5.4
 */
@ExtendWith(MockitoExtension.class)
class NodeOneTest {

    @Mock
    private ChatService chatService;

    @Test
    void process_shouldCallChatServiceAndStoreResult() {
        // Arrange
        String userInput = "测试输入内容";
        String expectedPrompt = "请对以下内容进行初步分析：" + userInput;
        String mockResponse = "这是大模型的分析结果";

        when(chatService.chat(expectedPrompt)).thenReturn(mockResponse);

        NodeOne nodeOne = new NodeOne(chatService);
        WorkflowContext context = new WorkflowContext(userInput);

        // Act
        WorkflowContext result = nodeOne.process(context);

        // Assert
        assertSame(context, result);
        assertEquals(mockResponse, result.getNodeOneOutput());
        verify(chatService, times(1)).chat(expectedPrompt);
        verifyNoMoreInteractions(chatService);
    }

    @Test
    void getName_shouldReturnNodeOne() {
        NodeOne nodeOne = new NodeOne(chatService);
        assertEquals("NodeOne", nodeOne.getName());
    }
}
