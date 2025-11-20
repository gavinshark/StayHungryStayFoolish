#!/bin/bash

echo "=== 编译Agent工具 ==="
echo ""

echo "1. 编译Agent..."
javac ThreadControlAgent.java

echo "2. 创建Agent JAR..."
jar cfm ThreadControlAgent.jar MANIFEST.MF ThreadControlAgent*.class

echo "3. 编译注入工具..."
javac -cp $JAVA_HOME/lib/tools.jar:. AttachAndInject.java

echo ""
echo "构建完成！"
echo ""
echo "使用方法："
echo "1. 启动目标程序: java ThreadDumpDemo"
echo "2. 获取PID（程序会显示）"
echo "3. 执行命令:"
echo ""
echo "   创建线程: java -cp \$JAVA_HOME/lib/tools.jar:. AttachAndInject <PID> create <线程名> [秒数]"
echo "   停止线程: java -cp \$JAVA_HOME/lib/tools.jar:. AttachAndInject <PID> stop <线程名>"
echo "   列出线程: java -cp \$JAVA_HOME/lib/tools.jar:. AttachAndInject <PID> list"
echo ""
echo "示例:"
echo "  java -cp \$JAVA_HOME/lib/tools.jar:. AttachAndInject 12345 create TestThread 60"
echo "  java -cp \$JAVA_HOME/lib/tools.jar:. AttachAndInject 12345 stop TestThread"
echo "  java -cp \$JAVA_HOME/lib/tools.jar:. AttachAndInject 12345 list"
