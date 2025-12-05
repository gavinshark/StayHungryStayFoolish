import com.sun.tools.attach.VirtualMachine;
import com.sun.tools.attach.VirtualMachineDescriptor;
import java.io.*;
import java.util.*;

/**
 * 方法统计收集器 - 使用JVM内置的Attach机制控制线程
 * 
 * 功能：
 * 1. 使用Dynamic Attach附加ThreadControlAgent
 * 2. 通过Agent启动非daemon线程
 * 3. 等待指定时间
 * 4. 通过Agent停止非daemon线程
 */
public class MethodStatsCollector {
    
    private static final String THREAD_NAME = "StatsCollector";
    private static final long THREAD_INTERVAL = 1000; // 1秒
    
    private VirtualMachine vm;
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java MethodStatsCollector <pid> [duration_seconds]");
            System.out.println();
            System.out.println("This tool uses JVM's built-in Attach mechanism");
            System.out.println("to control threads via ThreadControlAgent");
            System.out.println();
            System.out.println("Examples:");
            System.out.println("  java MethodStatsCollector 12345        - Run for 30 seconds");
            System.out.println("  java MethodStatsCollector 12345 60     - Run for 60 seconds");
            System.out.println();
            System.out.println("Available Java processes:");
            listJavaProcesses();
            return;
        }
        
        String pid = args[0];
        int duration = args.length > 1 ? Integer.parseInt(args[1]) : 30;
        
        MethodStatsCollector collector = new MethodStatsCollector();
        
        try {
            System.out.println("=== Method Statistics Collector ===");
            System.out.println("Target PID: " + pid);
            System.out.println("Duration: " + duration + " seconds");
            System.out.println();
            
            // 步骤1: Attach并启动非daemon线程
            collector.attachAndStartThread(pid);
            
            // 步骤2: 等待指定时间
            collector.waitForDuration(duration);
            
            // 步骤3: 停止非daemon线程
            collector.stopThread(pid);
            
            // 步骤4: 清理资源
            collector.cleanup();
            
            System.out.println("\n=== Completed ===");
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * 列出所有Java进程
     */
    private static void listJavaProcesses() {
        List<VirtualMachineDescriptor> vms = VirtualMachine.list();
        if (vms.isEmpty()) {
            System.out.println("No Java processes found");
            return;
        }
        
        System.out.printf("%-10s %s\n", "PID", "Display Name");
        System.out.println("--------------------------------------------------------------");
        for (VirtualMachineDescriptor vmd : vms) {
            System.out.printf("%-10s %s\n", vmd.id(), vmd.displayName());
        }
    }
    
    /**
     * 步骤1: Attach并启动非daemon线程
     */
    private void attachAndStartThread(String pid) throws Exception {
        System.out.println("Step 1: Attaching to JVM and starting non-daemon thread...");
        
        // 获取Agent JAR的绝对路径
        String agentJar = new File("../agent-tool/agent/ThreadControlAgent.jar").getAbsolutePath();
        
        // Attach到目标JVM
        vm = VirtualMachine.attach(pid);
        
        // 构造命令：add:<name>:<daemon>:<interval>
        String command = "add:" + THREAD_NAME + ":false:" + THREAD_INTERVAL;
        System.out.println("  Command: " + command);
        
        // 加载Agent并执行命令
        vm.loadAgent(agentJar, command);
        
        System.out.println("✓ Non-daemon thread started: " + THREAD_NAME);
        System.out.println();
        
        // 等待线程启动
        Thread.sleep(1000);
    }
    
    /**
     * 步骤2: 等待指定时间
     */
    private void waitForDuration(int seconds) {
        System.out.println("Step 2: Waiting for " + seconds + " seconds...");
        
        try {
            for (int i = 1; i <= seconds; i++) {
                if (i % 5 == 0) {
                    System.out.println("  Progress: " + i + "s / " + seconds + "s");
                }
                Thread.sleep(1000);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println("✓ Wait completed");
        System.out.println();
    }
    
    /**
     * 步骤3: 停止非daemon线程
     */
    private void stopThread(String pid) throws Exception {
        System.out.println("Step 3: Stopping non-daemon thread...");
        
        String agentJar = new File("../agent-tool/agent/ThreadControlAgent.jar").getAbsolutePath();
        
        // 构造停止命令
        String command = "stop:" + THREAD_NAME;
        System.out.println("  Command: " + command);
        
        // 加载Agent并执行停止命令
        vm.loadAgent(agentJar, command);
        
        System.out.println("✓ Non-daemon thread stopped: " + THREAD_NAME);
        System.out.println();
        
        // 等待线程停止
        Thread.sleep(1000);
    }
    
    /**
     * 步骤4: 清理资源
     */
    private void cleanup() {
        System.out.println("Step 4: Cleaning up...");
        
        try {
            if (vm != null) {
                vm.detach();
            }
            System.out.println("✓ Detached from JVM");
        } catch (Exception e) {
            System.err.println("Error during cleanup: " + e.getMessage());
        }
    }
}
