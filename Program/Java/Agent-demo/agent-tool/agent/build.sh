#!/bin/bash

echo "=== Building Thread Control Agent ==="
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

# 编译Agent
echo "Compiling ThreadControlAgent..."
javac ThreadControlAgent.java

if [ $? -ne 0 ]; then
    echo "✗ Failed to compile ThreadControlAgent"
    exit 1
fi
echo "✓ ThreadControlAgent compiled"

# 创建Agent JAR
echo "Creating agent JAR..."
jar cvfm ThreadControlAgent.jar MANIFEST.MF ThreadControlAgent*.class

if [ $? -ne 0 ]; then
    echo "✗ Failed to create agent JAR"
    exit 1
fi
echo "✓ Agent JAR created: ThreadControlAgent.jar"

# 编译MethodTrackerAgent
echo "Compiling MethodTrackerAgent..."
javac MethodTrackerAgent.java

if [ $? -ne 0 ]; then
    echo "✗ Failed to compile MethodTrackerAgent"
    exit 1
fi
echo "✓ MethodTrackerAgent compiled"

# 创建MethodTrackerAgent JAR
echo "Creating MethodTrackerAgent JAR..."
jar cvfm MethodTrackerAgent.jar MANIFEST-MethodTracker.MF MethodTrackerAgent*.class

if [ $? -ne 0 ]; then
    echo "✗ Failed to create MethodTrackerAgent JAR"
    exit 1
fi
echo "✓ MethodTrackerAgent JAR created: MethodTrackerAgent.jar"

echo
echo "=== Build completed successfully! ==="
echo
echo "Agent JARs created:"
echo "  1. ThreadControlAgent.jar    - Thread control agent"
echo "  2. MethodTrackerAgent.jar    - Method tracking agent (Socket-based)"
echo
echo "To use the method statistics tool:"
echo "  cd ../../statistics"
echo "  ./build.sh"
echo "  java -cp .:\$JAVA_HOME/lib/tools.jar MethodStatsClient <pid> [port] [wait_seconds]"
