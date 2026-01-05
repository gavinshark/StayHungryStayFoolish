# Build 目录说明

本目录包含 C++ Gateway 项目的构建脚本和配置文件。

## 文件说明

| 文件 | 用途 | 平台 |
|------|------|------|
| `Makefile` | Make 构建配置 | Linux, macOS, Windows (MinGW) |
| `CMakeLists.txt` | CMake 构建配置 | 跨平台 |
| `build.sh` | CMake 自动化构建脚本 | Linux, macOS |
| `build.bat` | CMake 自动化构建脚本 | Windows |

## 前置要求

在构建之前，请确保已安装第三方依赖：

```bash
# 从项目根目录运行
./third_party/install_deps.sh
```

详细说明请参考 `third_party/README.md`。

## 构建方法

### 方法 1: 使用 CMake（推荐）

CMake是推荐的构建方式，支持第三方库集成。

#### Linux / macOS

```bash
# 使用自动化脚本
./build/build.sh

# 或手动执行
cd build
cmake -DCMAKE_BUILD_TYPE=Release .
make
```

#### Windows

```cmd
REM 使用自动化脚本
build\build.bat

REM 或手动执行（MSVC）
cd build
cmake -DCMAKE_BUILD_TYPE=Release .
cmake --build . --config Release

REM 或手动执行（MinGW）
cd build
cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release .
mingw32-make
```

**编译产物**:
- 可执行文件: `output/gateway` (Linux/macOS) 或 `output/gateway.exe` (Windows)

### 方法 2: 使用 Makefile（已弃用）

**注意**: Makefile不包含新的第三方库依赖，建议使用CMake。

#### Linux / macOS

```bash
# 从项目根目录
./make.sh

# 或从 build 目录
cd build
make
```

#### Windows (MinGW)

```cmd
cd build
mingw32-make
```

## 清理构建文件

### 使用 Makefile

```bash
# 从项目根目录
./make.sh clean

# 或从 build 目录
cd build
make clean
```

### 使用 CMake

```bash
# Linux/macOS
./build/build.sh clean

# Windows
build\build.bat clean
```

## 输出目录结构

```
output/
├── obj/                    # 目标文件 (.o)
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

## 编译器要求

| 平台 | 编译器 | 最低版本 |
|------|--------|---------|
| Linux | GCC | 7.0+ |
| macOS | Clang | 5.0+ |
| Windows | MSVC | 2017+ |
| Windows | MinGW (GCC) | 7.0+ |

## 第三方库配置

CMakeLists.txt会自动检测以下第三方库：

- **Asio**: `third_party/asio/asio/include`
- **nlohmann/json**: `third_party/json/include`
- **spdlog**: `third_party/spdlog/include`
- **http-parser** (可选): `third_party/http-parser`

如果CMake找不到这些库，会显示警告信息。

## 常见问题

### Q: CMake找不到第三方库？
A: 运行依赖安装脚本:
```bash
./third_party/install_deps.sh
```

### Q: 编译时找不到头文件？
A: 确保 `include/` 目录存在且包含所有必要的头文件，并且已安装第三方依赖。

### Q: 链接时出现 undefined reference 错误？
A: 
- Linux/macOS: 确保链接了 `-pthread`
- Windows: 确保链接了 `ws2_32` 库

### Q: Windows 上编译失败？
A: 
1. 确保安装了 Visual Studio 或 MinGW
2. 对于 MSVC，需要在 "Developer Command Prompt" 中运行
3. 对于 MinGW，确保 `g++` 和 `mingw32-make` 在 PATH 中

### Q: macOS 上编译失败？
A: 确保安装了 Xcode Command Line Tools:
```bash
xcode-select --install
```

## 构建选项

### Makefile 变量

可以通过命令行覆盖 Makefile 变量：

```bash
# 使用不同的编译器
make CXX=clang++

# 添加调试符号
make CXXFLAGS="-std=c++17 -g -Wall -Wextra -I../include"

# 指定优化级别
make CXXFLAGS="-std=c++17 -O3 -Wall -Wextra -I../include"
```

### CMake 选项

```bash
# Debug 构建
cmake -DCMAKE_BUILD_TYPE=Debug .

# Release 构建（默认）
cmake -DCMAKE_BUILD_TYPE=Release .

# 指定编译器
cmake -DCMAKE_CXX_COMPILER=clang++ .

# 详细输出
cmake --build . --verbose
```

## 性能优化

### 编译优化级别

- `-O0`: 无优化（调试用）
- `-O1`: 基本优化
- `-O2`: 推荐的优化级别
- `-O3`: 最高优化级别
- `-Os`: 优化代码大小

### 并行编译

```bash
# Makefile (使用 4 个并行任务)
make -j4

# CMake
cmake --build . --parallel 4
```

## 交叉编译

### 为 ARM Linux 编译

```bash
# 设置交叉编译工具链
export CXX=arm-linux-gnueabihf-g++
make
```

### 为 Windows 编译（在 Linux 上）

```bash
# 使用 MinGW 交叉编译器
export CXX=x86_64-w64-mingw32-g++
make
```

---

**最后更新**: 2024-12-06
