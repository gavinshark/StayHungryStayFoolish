import java.lang.instrument.Instrumentation;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 线程控制Agent - 用于动态添加或退出daemon线程
 */
public class ThreadControlAgent {
    
    private static final Map<String, Thread> managedThreads = new ConcurrentHashMap<>();
    private static volatile boolean initialized = false;
    
    /**
     * Agent入口点 - 用于动态attach
     */
    public static void agentmain(String agentArgs, Instrumentation inst) {
        System.out.println("ThreadControlAgent attached dynamically");
        initAgent(agentArgs);
    }
    
    /**
     * Agent入口点 - 用于启动时加载
     */
    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("ThreadControlAgent loaded at startup");
        initAgent(agentArgs);
    }
    
    private static void initAgent(String agentArgs) {
        if (initialized) {
            System.out.println("ThreadControlAgent already initialized");
            handleCommand(agentArgs);
            return;
        }
        
        initialized = true;
        
        // 注册关闭钩子
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\n=== ThreadControlAgent Shutting Down ===");
            stopAllThreads();
        }));
        
        System.out.println("ThreadControlAgent initialized");
        
        // 处理启动参数
        if (agentArgs != null && !agentArgs.isEmpty()) {
            handleCommand(agentArgs);
        }
    }
    
    /**
     * 处理命令
     */
    private static void handleCommand(String command) {
        if (command == null || command.isEmpty()) {
            return;
        }
        
        String[] parts = command.split(":");
        String action = parts[0];
        
        switch (action) {
            case "add":
                if (parts.length >= 2) {
                    String threadName = parts[1];
                    boolean daemon = parts.length >= 3 ? Boolean.parseBoolean(parts[2]) : true;
                    long interval = parts.length >= 4 ? Long.parseLong(parts[3]) : 1000;
                    addThread(threadName, daemon, interval);
                }
                break;
                
            case "stop":
                if (parts.length >= 2) {
                    String threadName = parts[1];
                    stopThread(threadName);
                }
                break;
                
            case "list":
                listThreads();
                break;
                
            case "stopall":
                stopAllThreads();
                break;
                
            default:
                System.out.println("Unknown command: " + action);
                printUsage();
        }
    }
    
    /**
     * 添加一个新线程
     */
    public static void addThread(String name, boolean daemon, long intervalMs) {
        if (managedThreads.containsKey(name)) {
            System.out.println("Thread already exists: " + name);
            return;
        }
        
        Thread thread = new Thread(() -> {
            System.out.println("Thread started: " + name + " (daemon=" + daemon + ")");
            long iteration = 0;
            
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    iteration++;
                    System.out.println("[" + name + "] Iteration: " + iteration + 
                                     " (daemon=" + daemon + ")");
                    Thread.sleep(intervalMs);
                } catch (InterruptedException e) {
                    System.out.println("Thread interrupted: " + name);
                    break;
                }
            }
            
            System.out.println("Thread stopped: " + name);
        });
        
        thread.setName(name);
        thread.setDaemon(daemon);
        managedThreads.put(name, thread);
        thread.start();
        
        System.out.println("✓ Thread added: " + name + " (daemon=" + daemon + 
                         ", interval=" + intervalMs + "ms)");
    }
    
    /**
     * 停止指定线程
     */
    public static void stopThread(String name) {
        Thread thread = managedThreads.get(name);
        if (thread == null) {
            System.out.println("Thread not found: " + name);
            return;
        }
        
        thread.interrupt();
        managedThreads.remove(name);
        
        try {
            thread.join(5000);
            System.out.println("✓ Thread stopped: " + name);
        } catch (InterruptedException e) {
            System.out.println("Failed to stop thread: " + name);
        }
    }
    
    /**
     * 停止所有管理的线程
     */
    public static void stopAllThreads() {
        System.out.println("Stopping all managed threads...");
        
        for (Map.Entry<String, Thread> entry : managedThreads.entrySet()) {
            String name = entry.getKey();
            Thread thread = entry.getValue();
            
            System.out.println("Stopping thread: " + name);
            thread.interrupt();
            
            try {
                thread.join(3000);
            } catch (InterruptedException e) {
                System.out.println("Timeout waiting for thread: " + name);
            }
        }
        
        managedThreads.clear();
        System.out.println("All threads stopped");
    }
    
    /**
     * 列出所有管理的线程
     */
    public static void listThreads() {
        System.out.println("\n=== Managed Threads ===");
        
        if (managedThreads.isEmpty()) {
            System.out.println("No managed threads");
            return;
        }
        
        System.out.printf("%-20s %-10s %-10s\n", "Name", "Daemon", "State");
        System.out.println("--------------------------------------------");
        
        for (Map.Entry<String, Thread> entry : managedThreads.entrySet()) {
            Thread thread = entry.getValue();
            System.out.printf("%-20s %-10s %-10s\n", 
                            thread.getName(), 
                            thread.isDaemon(), 
                            thread.getState());
        }
        
        System.out.println();
    }
    
    /**
     * 打印使用说明
     */
    private static void printUsage() {
        System.out.println("\nThreadControlAgent Commands:");
        System.out.println("  add:<name>:<daemon>:<interval>  - Add a new thread");
        System.out.println("  stop:<name>                     - Stop a thread");
        System.out.println("  list                            - List all managed threads");
        System.out.println("  stopall                         - Stop all threads");
        System.out.println();
        System.out.println("Examples:");
        System.out.println("  add:worker1:true:1000   - Add daemon thread with 1s interval");
        System.out.println("  add:worker2:false:2000  - Add non-daemon thread with 2s interval");
        System.out.println("  stop:worker1            - Stop worker1 thread");
        System.out.println("  list                    - List all threads");
    }
}