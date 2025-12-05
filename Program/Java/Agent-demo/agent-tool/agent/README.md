# Thread Control Agent

这是一个Java Agent，用于动态添加或退出daemon/non-daemon线程到运行中的JDK 8应用程序。

## 功能特性

- 动态附加到运行中的Java进程
- 添加daemon线程或non-daemon线程
- 停止指定的线程
- 列出所有管理的线程
- 停止所有管理的线程
- 支持启动时加载或运行时动态附加

## 编译

```bash
./build.sh
```

编译后会生成：
- `ThreadControlAgent.jar` - Agent JAR包
- `AttachAndControl.class` - 动态附加和控制工具

## 使用方法

### 方式1：启动时加载Agent

```bash
java -javaagent:ThreadControlAgent.jar -cp <your-app-classpath> YourMainClass
```

启动时添加线程：
```bash
java -javaagent:ThreadControlAgent.jar=add:worker1:true:1000 -cp <classpath> YourMainClass
```

### 方式2：动态附加到运行中的进程

1. 查看Java进程列表：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl
```

2. 附加Agent到目标进程：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid>
```

3. 添加daemon线程（每1秒执行一次）：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid> add:worker1:true:1000
```

4. 添加non-daemon线程（每2秒执行一次）：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid> add:worker2:false:2000
```

5. 停止指定线程：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid> stop:worker1
```

6. 列出所有管理的线程：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid> list
```

7. 停止所有管理的线程：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid> stopall
```

## 命令格式

### add命令
格式：`add:<name>:<daemon>:<interval>`

参数：
- `name` - 线程名称
- `daemon` - 是否为daemon线程（true/false）
- `interval` - 执行间隔（毫秒）

示例：
- `add:worker1:true:1000` - 添加名为worker1的daemon线程，每1秒执行一次
- `add:worker2:false:2000` - 添加名为worker2的non-daemon线程，每2秒执行一次

### stop命令
格式：`stop:<name>`

参数：
- `name` - 要停止的线程名称

示例：
- `stop:worker1` - 停止名为worker1的线程

### list命令
格式：`list`

列出所有由Agent管理的线程及其状态。

### stopall命令
格式：`stopall`

停止所有由Agent管理的线程。

## Daemon线程 vs Non-Daemon线程

### Daemon线程
- 后台线程，不会阻止JVM退出
- 当所有non-daemon线程结束时，JVM会自动退出，daemon线程也会被强制终止
- 适合用于后台服务、监控等任务

### Non-Daemon线程
- 前台线程，会阻止JVM退出
- JVM会等待所有non-daemon线程结束后才退出
- 适合用于重要的业务逻辑处理

## 输出示例

添加线程时：
```
ThreadControlAgent attached dynamically
ThreadControlAgent initialized
✓ Thread added: worker1 (daemon=true, interval=1000ms)
Thread started: worker1 (daemon=true)
[worker1] Iteration: 1 (daemon=true)
[worker1] Iteration: 2 (daemon=true)
```

列出线程时：
```
=== Managed Threads ===
Name                 Daemon     State     
--------------------------------------------
worker1              true       TIMED_WAITING
worker2              false      TIMED_WAITING
```

停止线程时：
```
Thread interrupted: worker1
Thread stopped: worker1
✓ Thread stopped: worker1
```

## 注意事项

1. 需要JDK 8（包含tools.jar）
2. 需要与目标进程相同的用户权限
3. Daemon线程会在JVM退出时被强制终止
4. Non-daemon线程会阻止JVM正常退出，需要手动停止
5. 线程名称必须唯一

## 使用场景

- 动态添加监控线程
- 动态添加定时任务
- 测试daemon线程和non-daemon线程的行为差异
- 在运行时调整应用的线程配置
- 调试线程相关问题
