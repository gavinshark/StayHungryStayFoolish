package com.example.workflow.model;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * 工作流上下文，在节点间传递数据
 */
public class WorkflowContext {
    private final String input;
    private String nodeOneOutput;
    private String nodeTwoOutput;
    private String finalOutput;
    private final Map<String, Object> metadata;
    private final Instant createdAt;

    public WorkflowContext(String input) {
        this.input = input;
        this.metadata = new HashMap<>();
        this.createdAt = Instant.now();
    }

    // Getters and Setters
    public String getInput() {
        return input;
    }

    public String getNodeOneOutput() {
        return nodeOneOutput;
    }

    public void setNodeOneOutput(String output) {
        this.nodeOneOutput = output;
    }

    public String getNodeTwoOutput() {
        return nodeTwoOutput;
    }

    public void setNodeTwoOutput(String output) {
        this.nodeTwoOutput = output;
    }

    public String getFinalOutput() {
        return finalOutput;
    }

    public void setFinalOutput(String output) {
        this.finalOutput = output;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void putMetadata(String key, Object value) {
        metadata.put(key, value);
    }

    public Object getMetadata(String key) {
        return metadata.get(key);
    }

    public Map<String, Object> getAllMetadata() {
        return new HashMap<>(metadata);
    }
}
