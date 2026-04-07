package com.example.workflow.engine;

import com.example.workflow.exception.WorkflowException;
import com.example.workflow.model.WorkflowContext;
import com.example.workflow.node.NodeOne;
import com.example.workflow.node.NodeThree;
import com.example.workflow.node.NodeTwo;
import com.example.workflow.node.WorkflowNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 工作流引擎，协调节点按顺序执行
 * 按 NodeOne → NodeTwo → NodeThree 顺序执行，在节点间传递 WorkflowContext
 */
@Service
public class WorkflowEngine {

    private static final Logger log = LoggerFactory.getLogger(WorkflowEngine.class);

    private final List<WorkflowNode> nodes;

    public WorkflowEngine(NodeOne nodeOne, NodeTwo nodeTwo, NodeThree nodeThree) {
        this.nodes = List.of(nodeOne, nodeTwo, nodeThree);
    }

    /**
     * 执行工作流
     * @param input 初始输入
     * @return 最终结果
     * @throws WorkflowException 执行失败时抛出
     */
    public String execute(String input) throws WorkflowException {
        WorkflowContext context = new WorkflowContext(input);

        for (WorkflowNode node : nodes) {
            try {
                log.info("Executing node: {}", node.getName());
                context = node.process(context);
            } catch (Exception e) {
                log.error("Node {} failed: {}", node.getName(), e.getMessage());
                throw new WorkflowException("Workflow failed at node: " + node.getName(), e);
            }
        }

        return context.getFinalOutput();
    }
}
