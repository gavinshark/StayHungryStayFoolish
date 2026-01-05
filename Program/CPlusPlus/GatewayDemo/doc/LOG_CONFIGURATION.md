# 日志配置说明

## ✅ 已完成的修改

### 1. 配置文件更新

**文件**: `config/config.json`

日志文件路径已更新为：
```json
{
  "log_file": "log/gateway.log"
}
```

### 2. Logger 自动创建目录

**文件**: `src/logger.cpp`

已添加自动创建 log 目录的功能：

```cpp
// 创建日志目录（如果需要）
size_t last_slash = log_file.find_last_of("/\\");
if (last_slash != std::string::npos) {
    std::string log_dir = log_file.substr(0, last_slash);
    // 尝试创建目录（如果已存在会失败，但不影响）
    mkdir(log_dir.c_str(), 0755);
}
```

**特性**:
- 自动从日志文件路径中提取目录
- 支持 Linux/macOS 和 Windows 路径分隔符
- 如果目录已存在，不会报错
- 跨平台支持（使用条件编译）

### 3. .gitignore 更新

**文件**: `.gitignore`

已添加 log 目录到忽略列表：
```
# 日志文件
*.log
log/
```

## 📁 目录结构

```
cpp-gateway/
├── log/                    ← 日志目录（自动创建）
│   └── gateway.log         ← 日志文件
├── config/
│   └── config.json         ← 配置文件（已更新）
├── src/
│   └── logger.cpp          ← Logger 实现（已更新）
└── ...
```

## 🚀 使用方法

### 1. 编译项目

```bash
./make.sh
```

### 2. 启动网关

```bash
./output/gateway config/config.json
```

网关启动时会：
1. 自动创建 `log/` 目录（如果不存在）
2. 在 `log/gateway.log` 中写入日志
3. 同时在控制台输出日志

### 3. 查看日志

```bash
# 查看完整日志
cat log/gateway.log

# 实时查看日志
tail -f log/gateway.log

# 查看最后 50 行
tail -n 50 log/gateway.log
```

## 📝 日志格式

日志格式：
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] Message
```

示例：
```
[2024-12-06 16:40:00] [INFO] Logger initialized with level: info
[2024-12-06 16:40:00] [INFO] === Gateway Starting ===
[2024-12-06 16:40:00] [INFO] Version: 1.0.0
[2024-12-06 16:40:00] [INFO] Listen Port: 8080
[2024-12-06 16:40:00] [INFO] Log Level: info
[2024-12-06 16:40:00] [INFO] Backend Timeout: 5000ms
[2024-12-06 16:40:00] [INFO] Routes configured: 3
[2024-12-06 16:40:01] [INFO] Request: GET /api/users
[2024-12-06 16:40:01] [DEBUG] Selected backend: http://localhost:9001
[2024-12-06 16:40:01] [INFO] Response: 200 OK
```

## ⚙️ 配置选项

### 日志级别

在 `config/config.json` 中配置：

```json
{
  "log_level": "debug"  // 可选: debug, info, warn, error
}
```

**级别说明**:
- `debug`: 显示所有日志（最详细）
- `info`: 显示信息、警告和错误
- `warn`: 显示警告和错误
- `error`: 只显示错误

### 日志文件路径

在 `config/config.json` 中配置：

```json
{
  "log_file": "log/gateway.log"  // 可以是任意路径
}
```

**支持的路径格式**:
- 相对路径: `log/gateway.log`
- 绝对路径: `/var/log/gateway/gateway.log`
- 子目录: `logs/2024/gateway.log`（会自动创建多级目录）

## 🔧 跨平台支持

### Linux / macOS

使用 POSIX `mkdir()` 函数：
```cpp
mkdir(log_dir.c_str(), 0755);
```

### Windows

使用 Windows `_mkdir()` 函数：
```cpp
#ifdef _WIN32
#include <direct.h>
#define mkdir(path, mode) _mkdir(path)
#endif
```

## 📊 日志输出

日志会同时输出到两个地方：

1. **控制台** - 实时查看
2. **文件** - 持久化存储（`log/gateway.log`）

## 🐛 故障排除

### 问题：日志文件未创建

**可能原因**:
1. 没有写入权限
2. 磁盘空间不足
3. 路径包含不存在的多级目录

**解决方案**:
```bash
# 手动创建 log 目录
mkdir -p log

# 检查权限
ls -ld log/

# 检查磁盘空间
df -h .
```

### 问题：日志文件为空

**可能原因**:
1. 网关未正常启动
2. 日志级别设置过高
3. 配置文件路径错误

**解决方案**:
```bash
# 检查网关是否运行
ps aux | grep gateway

# 检查配置文件
cat config/config.json

# 设置 debug 级别查看详细日志
# 修改 config.json: "log_level": "debug"
```

### 问题：权限被拒绝

**解决方案**:
```bash
# 给 log 目录添加写权限
chmod 755 log/

# 或者使用不同的日志路径
# 修改 config.json: "log_file": "/tmp/gateway.log"
```

## ✨ 优势

1. **自动创建目录** - 无需手动创建 log 目录
2. **跨平台支持** - Linux、macOS、Windows 都能正常工作
3. **双重输出** - 控制台和文件同时输出
4. **灵活配置** - 可以自定义日志路径和级别
5. **线程安全** - 多线程环境下日志不会混乱

## 📚 相关文件

- `config/config.json` - 日志配置
- `src/logger.cpp` - Logger 实现
- `include/logger.hpp` - Logger 接口
- `.gitignore` - Git 忽略配置

## 🎉 总结

✅ **日志配置已完成**

- 日志输出到 `log/` 目录
- 自动创建 log 目录
- 跨平台支持
- .gitignore 已更新
- 项目已重新编译

现在启动网关时，日志会自动输出到 `log/gateway.log` 文件中！

---

**更新日期**: 2024-12-06  
**状态**: ✅ 完成
