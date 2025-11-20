#!/bin/bash

# 自动查找 tools.jar
find_tools_jar() {
    # 优先使用 JAVA_HOME
    if [ -n "$JAVA_HOME" ] && [ -f "$JAVA_HOME/lib/tools.jar" ]; then
        echo "$JAVA_HOME/lib/tools.jar"
        return 0
    fi
    
    # 尝试从 java 命令推断
    JAVA_CMD=$(which java)
    if [ -n "$JAVA_CMD" ]; then
        # 解析符号链接
        JAVA_CMD=$(readlink -f "$JAVA_CMD" 2>/dev/null || realpath "$JAVA_CMD" 2>/dev/null || echo "$JAVA_CMD")
        JAVA_HOME_DETECTED=$(dirname $(dirname "$JAVA_CMD"))
        
        if [ -f "$JAVA_HOME_DETECTED/lib/tools.jar" ]; then
            echo "$JAVA_HOME_DETECTED/lib/tools.jar"
            return 0
        fi
    fi
    
    # macOS 特殊路径
    if [ "$(uname)" = "Darwin" ]; then
        MACOS_JDK=$(/usr/libexec/java_home 2>/dev/null)
        if [ -n "$MACOS_JDK" ] && [ -f "$MACOS_JDK/lib/tools.jar" ]; then
            echo "$MACOS_JDK/lib/tools.jar"
            return 0
        fi
    fi
    
    return 1
}

# 检查 JDK 版本
check_jdk_version() {
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    MAJOR_VERSION=$(echo "$JAVA_VERSION" | cut -d'.' -f1)
    
    # JDK 9+ 不需要 tools.jar
    if [ "$MAJOR_VERSION" -ge 9 ]; then
        echo "JDK $JAVA_VERSION (模块化，不需要 tools.jar)"
        return 2
    fi
    
    echo "JDK $JAVA_VERSION (需要 tools.jar)"
    return 0
}

# 主逻辑
echo "检测 JDK 环境..."
check_jdk_version
JDK_TYPE=$?

if [ $JDK_TYPE -eq 2 ]; then
    # JDK 9+
    CLASSPATH="."
else
    # JDK 8
    TOOLS_JAR=$(find_tools_jar)
    if [ $? -ne 0 ]; then
        echo "错误: 未找到 tools.jar"
        echo "请确保："
        echo "  1. 已安装 JDK (不是 JRE)"
        echo "  2. 设置了 JAVA_HOME 环境变量"
        exit 1
    fi
    echo "找到 tools.jar: $TOOLS_JAR"
    CLASSPATH="$TOOLS_JAR:."
fi

# 执行命令
if [ $# -lt 2 ]; then
    echo "用法:"
    echo "  $0 <PID> create <线程名> [秒数]"
    echo "  $0 <PID> stop <线程名>"
    echo "  $0 <PID> list"
    exit 1
fi

java -cp "$CLASSPATH" AttachAndInject "$@"
