import java.lang.instrument.Instrumentation;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class ThreadControlAgent {
    private static Map<String, Thread> managedThreads = new ConcurrentHashMap<>();
    
    // Agent入口方法（用于动态attach）
    public static void agentmain(String agentArgs, Instrumentation inst) {
        System.out.println("[Agent] 已注入到目标JVM");
        
        if (agentArgs == null || agentArgs.isEmpty()) {
            System.out.println("[Agent] 用法:");
            System.out.println("  创建线程: create,threadName,durationSeconds");
            System.out.println("  停止线程: stop,threadName");
            System.out.println("  列出线程: list");
            return;
        }
        
        String[] args = agentArgs.split(",");
        String command = args[0];
        
        switch (command) {
            case "create":
                if (args.length < 2) {
                    System.out.println("[Agent] 错误: 需要线程名称");
                    return;
                }
                String threadName = args[1];
                int duration = args.length > 2 ? Integer.parseInt(args[2]) : 30;
                createNonDaemonThread(threadName, duration);
                break;
                
            case "stop":
                if (args.length < 2) {
                    System.out.println("[Agent] 错误: 需要线程名称");
                    return;
                }
                stopThread(args[1]);
                break;
                
            case "list":
                listThreads();
                break;
                
            default:
                System.out.println("[Agent] 未知命令: " + command);
        }
    }
    
    private static void createNonDaemonThread(final String name, final int durationSeconds) {
        if (managedThreads.containsKey(name)) {
            System.out.println("[Agent] 错误: 线程 '" + name + "' 已存在");
            return;
        }
        
        Thread thread = new Thread(new Runnable() {
            public void run() {
                System.out.println("[Agent] 非daemon线程已创建: " + Thread.currentThread().getName());
                System.out.println("[Agent] 将在 " + durationSeconds + " 秒后退出");
                
                try {
                    Thread.sleep(durationSeconds * 1000L);
                    System.out.println("[Agent] 非daemon线程正常退出: " + Thread.currentThread().getName());
                } catch (InterruptedException e) {
                    System.out.println("[Agent] 非daemon线程被外部信号中断: " + Thread.currentThread().getName());
                }
                
                managedThreads.remove(Thread.currentThread().getName());
            }
        }, name);
        
        thread.setDaemon(false);  // 设置为非daemon线程
        managedThreads.put(name, thread);
        thread.start();
        
        System.out.println("[Agent] 线程已启动，当前管理的线程数: " + managedThreads.size());
    }
    
    private static void stopThread(String name) {
        Thread thread = managedThreads.get(name);
        if (thread == null) {
            System.out.println("[Agent] 错误: 线程 '" + name + "' 不存在");
            System.out.println("[Agent] 当前管理的线程: " + managedThreads.keySet());
            return;
        }
        
        System.out.println("[Agent] 正在中断线程: " + name);
        thread.interrupt();
        
        try {
            thread.join(5000);  // 等待最多5秒
            if (thread.isAlive()) {
                System.out.println("[Agent] 警告: 线程 '" + name + "' 未能在5秒内退出");
            } else {
                System.out.println("[Agent] 线程 '" + name + "' 已成功退出");
                managedThreads.remove(name);
            }
        } catch (InterruptedException e) {
            System.out.println("[Agent] 等待线程退出时被中断");
        }
    }
    
    private static void listThreads() {
        System.out.println("[Agent] 当前管理的非daemon线程数: " + managedThreads.size());
        if (managedThreads.isEmpty()) {
            System.out.println("[Agent] 无管理的线程");
        } else {
            System.out.println("[Agent] 线程列表:");
            for (Map.Entry<String, Thread> entry : managedThreads.entrySet()) {
                String name = entry.getKey();
                Thread thread = entry.getValue();
                System.out.println("  - " + name + " (状态: " + thread.getState() + 
                                 ", Daemon: " + thread.isDaemon() + 
                                 ", Alive: " + thread.isAlive() + ")");
            }
        }
    }
}
