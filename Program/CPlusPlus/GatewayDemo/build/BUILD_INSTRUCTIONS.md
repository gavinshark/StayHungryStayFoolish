# 构建说明

## 构建系统已就绪

build 目录已经创建完成，包含以下文件：

### 文件列表

1. **Makefile** - 跨平台 Make 构建脚本
   - 支持 Linux, macOS, Windows (MinGW)
   - 自动检测平台并使用相应的编译选项
   - 输出目录：`../output/`
   - 临时文件：`../output/obj/`

2. **CMakeLists.txt** - CMake 构建配置
   - 支持所有主流平台
   - 自动配置编译器和链接库
   - 输出目录：`../output/`

3. **build.sh** - Linux/macOS 自动化构建脚本
   - 使用 CMake 进行配置和构建
   - 支持 clean 参数清理构建文件

4. **build.bat** - Windows 自动化构建脚本
   - 自动检测 MSVC 或 MinGW 编译器
   - 支持 clean 参数清理构建文件

5. **README.md** - 详细的构建文档
   - 包含所有构建方法的说明
   - 常见问题解答
   - 性能优化建议

## 快速开始

### macOS / Linux

```bash
# 方法 1: 使用 Makefile（推荐）
./make.sh

# 方法 2: 使用 CMake
./build/build.sh

# 清理构建文件
./make.sh clean
# 或
./build/build.sh clean
```

### Windows

```cmd
REM 方法 1: 使用 Makefile (MinGW)
cd build
mingw32-make

REM 方法 2: 使用 CMake
build\build.bat

REM 清理构建文件
cd build
mingw32-make clean
REM 或
build\build.bat clean
```

## 输出目录结构

构建完成后，文件将输出到以下位置：

```
output/
├── obj/                    # 临时目标文件 (.o)
│   ├── main.o
│   ├── gateway.o
│   ├── http_server.o
│   ├── http_client.o
│   ├── http_parser.o
│   ├── config_manager.o
│   ├── logger.o
│   ├── request_router.o
│   └── load_balancer.o
└── gateway                 # 可执行文件 (Linux/macOS)
    或 gateway.exe          # 可执行文件 (Windows)
```

## 注意事项

### macOS 用户

如果遇到 Xcode 许可问题，请运行：

```bash
sudo xcodebuild -license accept
```

或者手动接受许可：

```bash
sudo xcodebuild -license
# 然后按空格键滚动到底部，输入 "agree"
```

### Windows 用户

确保已安装以下之一：
- Visual Studio 2017 或更高版本
- MinGW (GCC for Windows)

### Linux 用户

确保已安装 GCC 7.0 或更高版本：

```bash
sudo apt-get install build-essential  # Ubuntu/Debian
sudo yum groupinstall "Development Tools"  # CentOS/RHEL
```

## 验证构建

构建成功后，可以运行以下命令验证：

```bash
# 查看可执行文件
ls -lh output/gateway        # Linux/macOS
dir output\gateway.exe       # Windows

# 运行网关
./output/gateway config/config.json
```

## 构建特性

### 跨平台支持

- ✅ **Linux**: GCC 7+
- ✅ **macOS**: Clang 5+ (Xcode Command Line Tools)
- ✅ **Windows**: MSVC 2017+ 或 MinGW GCC 7+

### 编译选项

- C++17 标准
- 警告级别：`-Wall -Wextra` (GCC/Clang) 或 `/W4` (MSVC)
- 优化级别：Release 模式默认 `-O2`

### 平台特定链接库

- **Linux/macOS**: `-pthread` (多线程支持)
- **Windows**: `-lws2_32` (Socket 支持)

## 故障排除

### 问题：找不到编译器

**解决方案**:
- macOS: 安装 Xcode Command Line Tools: `xcode-select --install`
- Linux: 安装 GCC: `sudo apt-get install build-essential`
- Windows: 安装 Visual Studio 或 MinGW

### 问题：链接错误

**解决方案**:
- 确保所有源文件都存在于 `src/` 目录
- 确保所有头文件都存在于 `include/` 目录
- 运行 `make clean` 后重新编译

### 问题：权限错误

**解决方案**:
```bash
chmod +x make.sh
chmod +x build/build.sh
```

## 下一步

构建成功后，请参考以下文档：

1. **运行网关**: 查看 `README.md`
2. **测试网关**: 查看 `tests/EXAMPLES.md`
3. **配置网关**: 查看 `config/config.json`

---

**创建日期**: 2024-12-06
**状态**: ✅ 构建系统已就绪
