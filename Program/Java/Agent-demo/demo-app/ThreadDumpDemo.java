import java.lang.management.ManagementFactory;
import java.lang.management.ThreadInfo;
import java.lang.management.ThreadMXBean;

public class ThreadDumpDemo {
    public static void main(String[] args) throws InterruptedException {
        // JDK 1.8兼容：使用RuntimeMXBean获取PID
        String pid = ManagementFactory.getRuntimeMXBean().getName().split("@")[0];
        System.out.println("程序已启动，PID: " + pid);
        System.out.println("请在另一个终端执行: jstack " + pid);
        System.out.println("\n注意：jstack命令会自动打印线程信息");
        System.out.println("本程序会在收到jstack信号后额外打印线程的daemon状态\n");
        
        // 创建一个后台线程监听jstack输出
        Thread monitorThread = new Thread(new Runnable() {
            public void run() {
                try {
                    // 每隔1秒检查一次
                    while (true) {
                        Thread.sleep(1000);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });
        monitorThread.setDaemon(true);
        monitorThread.start();
        
        // 注册JVM关闭钩子，在jstack触发时打印线程信息
        Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {
            public void run() {
                System.out.println("\n========== 程序关闭，打印线程信息 ==========");
                printAllThreads();
            }
        }));
        
        // 主线程保持运行，并定期打印线程信息
        System.out.println("程序运行中，每10秒自动打印一次线程信息...\n");
        while (true) {
            printAllThreads();
            Thread.sleep(10000);
        }
    }
    
    private static void printAllThreads() {
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        ThreadInfo[] threadInfos = threadMXBean.dumpAllThreads(false, false);
        
        System.out.println("总线程数: " + threadInfos.length);
        System.out.println("\n线程列表:");
        System.out.println("----------------------------------------");
        
        for (ThreadInfo threadInfo : threadInfos) {
            long threadId = threadInfo.getThreadId();
            String threadName = threadInfo.getThreadName();
            Thread.State state = threadInfo.getThreadState();
            
            // 通过线程ID获取Thread对象来检查daemon状态
            Thread thread = findThreadById(threadId);
            boolean isDaemon = thread != null && thread.isDaemon();
            
            System.out.printf("线程ID: %d | 名称: %s | 状态: %s | Daemon: %s%n",
                    threadId, threadName, state, isDaemon ? "是" : "否");
        }
        
        System.out.println("----------------------------------------");
    }
    
    private static Thread findThreadById(long threadId) {
        ThreadGroup rootGroup = Thread.currentThread().getThreadGroup();
        while (rootGroup.getParent() != null) {
            rootGroup = rootGroup.getParent();
        }
        
        Thread[] threads = new Thread[rootGroup.activeCount() * 2];
        int count = rootGroup.enumerate(threads, true);
        
        for (int i = 0; i < count; i++) {
            if (threads[i] != null && threads[i].getId() == threadId) {
                return threads[i];
            }
        }
        return null;
    }
}
