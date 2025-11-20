# Java线程动态控制演示

通过Java Agent机制，在不修改目标程序的情况下，动态创建和控制非daemon线程。

## 目录结构

```
.
├── demo-app/           # 演示应用程序
│   └── ThreadDumpDemo.java
├── agent-tool/         # Agent工具
│   ├── ThreadControlAgent.java
│   ├── AttachAndInject.java
│   ├── MANIFEST.MF
│   ├── build.sh
│   └── run.sh         # 智能启动脚本
└── README.md
```

## 系统要求

- **JDK 8 或更高版本**（不支持 JRE）
- 设置 `JAVA_HOME` 环境变量（推荐）

### 安装 JDK

**macOS:**
```bash
brew install openjdk@8
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install openjdk-8-jdk
```

**Windows:**
下载并安装 OpenJDK: https://adoptium.net/

## 快速开始

### 1. 编译Agent工具

```bash
cd agent-tool
./build.sh
cd ..
```

### 2. 启动演示程序

```bash
cd demo-app
javac ThreadDumpDemo.java
java ThreadDumpDemo
```

程序会显示PID，例如：`程序已启动，PID: 12345`

### 3. 使用Agent工具控制线程

在另一个终端执行以下命令：

#### 方式1：使用智能启动脚本（推荐）

```bash
cd agent-tool

# 创建非daemon线程
./run.sh <PID> create MyThread 60

# 列出管理的线程
./run.sh <PID> list

# 通过外部信号停止线程
./run.sh <PID> stop MyThread
```

`run.sh` 会自动检测JDK版本并查找 `tools.jar`，无需手动配置。

#### 方式2：手动指定classpath（JDK 8）

```bash
cd agent-tool

# 创建非daemon线程
java -cp $JAVA_HOME/lib/tools.jar:. AttachAndInject <PID> create MyThread 60

# 列出管理的线程
java -cp $JAVA_HOME/lib/tools.jar:. AttachAndInject <PID> list

# 通过外部信号停止线程
java -cp $JAVA_HOME/lib/tools.jar:. AttachAndInject <PID> stop MyThread
```

**参数说明：**
- `<PID>`: 目标Java进程的进程ID
- `MyThread`: 线程名称（可自定义）
- `60`: 运行时长（秒）

## 功能特性

- ✅ 动态创建非daemon线程（不修改目标程序）
- ✅ 通过外部信号控制线程退出
- ✅ 查看所有管理的线程状态
- ✅ 基于标准JVM Attach API和Instrumentation机制

## 实现原理

1. **Attach API**: 动态连接到运行中的JVM进程
2. **Java Agent**: 注入代理代码到目标JVM
3. **Thread.interrupt()**: 通过中断信号控制线程退出
4. **线程管理**: Agent内部维护线程Map，支持创建、停止、列表操作

## 使用示例

```bash
# 1. 启动演示程序（终端1）
cd demo-app
java ThreadDumpDemo
# 输出: 程序已启动，PID: 12345

# 2. 创建一个运行60秒的非daemon线程（终端2）
cd agent-tool
./run.sh 12345 create WorkerThread 60
# 输出: [Agent] 非daemon线程已创建: WorkerThread

# 3. 查看管理的线程
./run.sh 12345 list
# 输出: [Agent] 线程列表:
#         - WorkerThread (状态: TIMED_WAITING, Daemon: false, Alive: true)

# 4. 提前停止线程
./run.sh 12345 stop WorkerThread
# 输出: [Agent] 线程 'WorkerThread' 已成功退出
```

## 注意事项

- **必须使用 JDK**（包含 tools.jar 或 jdk.attach 模块），JRE 不支持
- 目标 JVM 需要允许 attach 操作
- Attach Listener 线程会在首次 attach 后持续存在
- JDK 9+ 使用模块化系统，不需要 tools.jar
- 如果 `run.sh` 无法自动找到 tools.jar，请确保设置了 `JAVA_HOME` 环境变量
