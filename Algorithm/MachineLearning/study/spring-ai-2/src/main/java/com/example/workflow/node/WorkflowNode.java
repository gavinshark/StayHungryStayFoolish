package com.example.workflow.node;

import com.example.workflow.exception.WorkflowException;
import com.example.workflow.model.WorkflowContext;

/**
 * 工作流节点接口
 * 所有工作流节点的基础接口，定义了节点处理和标识的基本契约
 */
public interface WorkflowNode {
    
    /**
     * 处理工作流上下文
     * @param context 工作流上下文
     * @return 处理后的上下文
     * @throws WorkflowException 处理失败时抛出
     */
    WorkflowContext process(WorkflowContext context) throws WorkflowException;
    
    /**
     * 获取节点名称
     * @return 节点名称
     */
    String getName();
}
