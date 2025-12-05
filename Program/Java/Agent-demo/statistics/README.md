# Method Call Statistics Tool

这是一个方法调用统计工具，通过动态附加Agent和采样分析来统计Java应用程序的方法调用情况。

## 功能特性

1. **创建非daemon线程** - 在目标进程中创建一个非daemon线程用于标记统计过程
2. **扫描统计** - 通过JMX采样线程堆栈，统计各个方法的调用次数
3. **输出报告** - 按包、类、方法三个维度输出统计结果
4. **清理退出** - 停止非daemon线程并清理资源

## 工作原理

1. 使用Java Attach API动态附加ThreadControlAgent到目标进程
2. 通过Agent创建一个非daemon线程（StatisticsCollector）
3. 通过JMX连接到目标进程，定期采样线程堆栈
4. 统计每个方法在堆栈中出现的次数（采样计数）
5. 输出统计报告
6. 停止非daemon线程并退出

## 编译

```bash
./build.sh
```

## 使用方法

### 前提条件

1. 确保ThreadControlAgent已编译：
```bash
cd ../agent-tool/agent
./build.sh
cd ../../statistics
```

2. 启动目标应用（例如demo-app）：
```bash
cd ../demo-app
javac ThreadDumpDemo.java
java -cp . ThreadDumpDemo &
DEMO_PID=$!
echo "Demo PID: $DEMO_PID"
cd ../statistics
```

### 运行统计工具

默认扫描30秒：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid>
```

指定扫描时长（秒）：
```bash
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl <pid> 60
```

### 完整示例

```bash
# 1. 编译Agent
cd ../agent-tool/agent && ./build.sh && cd ../../statistics

# 2. 编译统计工具
./build.sh

# 3. 启动demo应用
cd ../demo-app
java -cp . ThreadDumpDemo &
DEMO_PID=$!
cd ../statistics

# 4. 运行统计（扫描30秒）
java -cp .:$JAVA_HOME/lib/tools.jar AttachAndControl $DEMO_PID 30

# 5. 停止demo应用
kill $DEMO_PID
```

## 输出报告

### 按包统计
显示每个包的总采样次数：
```
=== Statistics by Package ===
Package                                            Sample Count
-------------------------------------------------------------------
com.demo.service                                          8,234
com.demo.util                                             4,111
```

### 按类统计
显示每个类的总采样次数（Top 20）：
```
=== Statistics by Class ===
Class                                                      Sample Count
-----------------------------------------------------------------------------
UserService                                                       4,567
OrderService                                                      3,667
DataProcessor                                                     4,111
```

### 按方法统计
显示每个方法的采样次数（Top 30）：
```
=== Statistics by Method (Top 30) ===
Method                                                             Sample Count
-------------------------------------------------------------------------------------
UserService.getUser                                                       2,345
OrderService.createOrder                                                  1,890
DataProcessor.processData                                                 1,456
UserService.validateId                                                    1,234
OrderService.validateAmount                                                 987
```

### 总计信息
```
Total unique methods: 45
Total samples: 12,345
```

## 采样 vs 精确计数

### 本工具（采样方式）
- **原理**：定期采样线程堆栈，统计方法在堆栈中出现的次数
- **精度**：近似值，反映方法的相对热度
- **性能影响**：低（默认100ms采样间隔）
- **适用场景**：快速定位热点方法、性能分析

### 精确计数（字节码增强）
- **原理**：在每个方法入口插入计数代码
- **精度**：精确的调用次数
- **性能影响**：中-高
- **适用场景**：需要精确调用次数的场景

## 工作流程

```
1. Attach Agent → 创建非daemon线程
2. 连接JMX → 获取线程信息
3. 循环采样 → 统计方法调用
4. 输出报告 → 按包/类/方法展示
5. 停止线程 → 清理资源
6. 退出程序
```

## 参数说明

- `<pid>` - 目标Java进程的PID（必需）
- `[duration]` - 扫描时长（秒），默认30秒（可选）

## 注意事项

1. **非daemon线程**：工具会创建一个非daemon线程，确保在统计期间目标进程不会因为所有业务线程结束而退出
2. **采样间隔**：默认100ms，可以在代码中修改`SCAN_INTERVAL`常量
3. **性能影响**：采样方式对目标进程性能影响很小
4. **权限要求**：需要与目标进程相同的用户权限
5. **JDK版本**：需要JDK 8（包含tools.jar）

## 故障排除

**找不到ThreadControlAgent.jar**
- 确保先编译Agent：`cd ../agent-tool/agent && ./build.sh`

**权限被拒绝**
- 确保运行用户与目标进程用户相同

**连接失败**
- 检查目标进程是否正在运行
- 确认PID正确

**统计结果为空**
- 确认目标应用有业务代码在运行
- 增加扫描时长

## 扩展开发

可以根据需要修改以下参数：

```java
// 采样间隔（毫秒）
private static final long SCAN_INTERVAL = 100;

// 非daemon线程名称
private static final String THREAD_NAME = "StatisticsCollector";
```

也可以修改过滤规则，只统计特定包的方法：

```java
private boolean shouldIncludeMethod(String className) {
    return className.startsWith("com.myapp");
}
```
