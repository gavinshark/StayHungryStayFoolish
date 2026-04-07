package com.example.workflow.exception;

/**
 * 工作流异常类，用于表示工作流执行过程中的错误
 */
public class WorkflowException extends RuntimeException {
    
    private final String nodeName;
    
    /**
     * 创建工作流异常
     * @param message 异常消息
     */
    public WorkflowException(String message) {
        super(message);
        this.nodeName = null;
    }
    
    /**
     * 创建工作流异常，包含原因
     * @param message 异常消息
     * @param cause 原始异常
     */
    public WorkflowException(String message, Throwable cause) {
        super(message, cause);
        this.nodeName = extractNodeName(message);
    }
    
    /**
     * 获取发生异常的节点名称
     * @return 节点名称，如果无法解析则返回 null
     */
    public String getNodeName() {
        return nodeName;
    }
    
    /**
     * 从消息中提取节点名称
     * 支持 "node: NodeName" 或 "node:NodeName" 格式
     * @param message 异常消息
     * @return 节点名称，如果无法解析则返回 null
     */
    private static String extractNodeName(String message) {
        if (message == null || message.isEmpty()) {
            return null;
        }
        
        // 查找 "node:" 模式（不区分大小写）
        String lowerMessage = message.toLowerCase();
        int nodeIndex = lowerMessage.indexOf("node:");
        
        if (nodeIndex == -1) {
            return null;
        }
        
        // 提取 "node:" 后面的内容
        int startIndex = nodeIndex + "node:".length();
        
        // 跳过可能的空格
        while (startIndex < message.length() && message.charAt(startIndex) == ' ') {
            startIndex++;
        }
        
        if (startIndex >= message.length()) {
            return null;
        }
        
        // 找到节点名称的结束位置（遇到逗号、句号、空格或字符串结束）
        int endIndex = startIndex;
        while (endIndex < message.length()) {
            char c = message.charAt(endIndex);
            if (c == ',' || c == '.' || c == ' ' || c == '\n' || c == '\r') {
                break;
            }
            endIndex++;
        }
        
        if (endIndex > startIndex) {
            return message.substring(startIndex, endIndex);
        }
        
        return null;
    }
}
