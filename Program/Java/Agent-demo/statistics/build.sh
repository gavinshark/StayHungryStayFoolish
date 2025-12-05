#!/bin/bash

echo "=== Building Statistics Tool ==="
echo

# 检查JAVA_HOME
if [ -z "$JAVA_HOME" ]; then
    echo "Error: JAVA_HOME is not set"
    exit 1
fi

TOOLS_JAR="$JAVA_HOME/lib/tools.jar"
if [ ! -f "$TOOLS_JAR" ]; then
    echo "Error: tools.jar not found at $TOOLS_JAR"
    exit 1
fi

# 编译MethodStatsCollector
echo "Compiling MethodStatsCollector..."
javac -cp "$TOOLS_JAR" MethodStatsCollector.java

if [ $? -ne 0 ]; then
    echo "✗ Failed to compile MethodStatsCollector"
    exit 1
fi
echo "✓ MethodStatsCollector compiled"

echo
echo "=== Build completed successfully! ==="
echo
echo "Tool available:"
echo
echo "MethodStatsCollector (Uses JVM's built-in Attach mechanism like jmap/jstack):"
echo "  java -cp .:\$JAVA_HOME/lib/tools.jar MethodStatsCollector <pid> [duration]"
echo
echo "Examples:"
echo "  java -cp .:\$JAVA_HOME/lib/tools.jar MethodStatsCollector 12345"
echo "  java -cp .:\$JAVA_HOME/lib/tools.jar MethodStatsCollector 12345 60"
echo
echo "How it works:"
echo "  1. VirtualMachine.attach(pid) triggers Signal Dispatcher"
echo "  2. Signal Dispatcher creates Attach Listener thread"
echo "  3. Socket connection established between processes"
echo "  4. Commands sent via socket (like jmap/jstack)"
echo "  5. No custom agent or bytecode enhancement needed!"
