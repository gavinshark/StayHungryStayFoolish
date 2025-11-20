import com.sun.tools.attach.VirtualMachine;

public class AttachAndInject {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("用法:");
            System.out.println("  创建线程: java AttachAndInject <PID> create <线程名> [秒数]");
            System.out.println("  停止线程: java AttachAndInject <PID> stop <线程名>");
            System.out.println("  列出线程: java AttachAndInject <PID> list");
            System.out.println();
            System.out.println("示例:");
            System.out.println("  java AttachAndInject 12345 create MyThread 60");
            System.out.println("  java AttachAndInject 12345 stop MyThread");
            System.out.println("  java AttachAndInject 12345 list");
            return;
        }
        
        String pid = args[0];
        String command = args[1];
        
        try {
            System.out.println("正在attach到进程: " + pid);
            VirtualMachine vm = VirtualMachine.attach(pid);
            
            String agentPath = System.getProperty("user.dir") + "/ThreadControlAgent.jar";
            String agentArgs;
            
            switch (command) {
                case "create":
                    if (args.length < 3) {
                        System.err.println("错误: 需要线程名称");
                        return;
                    }
                    String threadName = args[2];
                    String duration = args.length > 3 ? args[3] : "30";
                    agentArgs = "create," + threadName + "," + duration;
                    System.out.println("创建非daemon线程: " + threadName + " (持续 " + duration + " 秒)");
                    break;
                    
                case "stop":
                    if (args.length < 3) {
                        System.err.println("错误: 需要线程名称");
                        return;
                    }
                    agentArgs = "stop," + args[2];
                    System.out.println("停止线程: " + args[2]);
                    break;
                    
                case "list":
                    agentArgs = "list";
                    System.out.println("列出管理的线程");
                    break;
                    
                default:
                    System.err.println("未知命令: " + command);
                    return;
            }
            
            System.out.println("正在加载Agent: " + agentPath);
            vm.loadAgent(agentPath, agentArgs);
            vm.detach();
            
            System.out.println("命令已成功执行！");
            
        } catch (Exception e) {
            System.err.println("执行失败: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
