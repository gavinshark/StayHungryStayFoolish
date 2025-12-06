# 第三方依赖库

本项目使用以下第三方库：

## 依赖列表

### 1. Asio (standalone)
- **版本**: 1.28.0+
- **类型**: Header-only
- **用途**: 跨平台异步I/O网络库
- **许可证**: Boost Software License
- **安装位置**: `third_party/asio/`

### 2. nlohmann/json
- **版本**: 3.11.0+
- **类型**: Header-only
- **用途**: 现代C++ JSON解析库
- **许可证**: MIT
- **安装位置**: `third_party/json/`

### 3. spdlog
- **版本**: 1.12.0+
- **类型**: Header-only
- **用途**: 快速的C++日志库
- **许可证**: MIT
- **安装位置**: `third_party/spdlog/`

### 4. http-parser (可选)
- **版本**: 2.9.4+
- **类型**: C library
- **用途**: HTTP协议解析
- **许可证**: MIT
- **安装位置**: `third_party/http-parser/`

## 安装方法

### 方法1: 使用安装脚本（推荐）

#### Linux / macOS
```bash
# 从项目根目录运行
./third_party/install_deps.sh
```

#### Windows
```cmd
REM 从项目根目录运行
third_party\install_deps.bat
```

### 方法2: 手动安装

#### Asio
```bash
cd third_party
git clone https://github.com/chriskohlhoff/asio.git
cd asio
git checkout asio-1-28-0  # 或最新稳定版本
```

#### nlohmann/json
```bash
cd third_party
git clone https://github.com/nlohmann/json.git
cd json
git checkout v3.11.3  # 或最新稳定版本
```

#### spdlog
```bash
cd third_party
git clone https://github.com/gabime/spdlog.git
cd spdlog
git checkout v1.12.0  # 或最新稳定版本
```

#### http-parser (可选)
```bash
cd third_party
git clone https://github.com/nodejs/http-parser.git
cd http-parser
git checkout v2.9.4  # 或最新稳定版本
```

### 方法3: 使用包管理器

#### vcpkg (Windows/Linux/macOS)
```bash
vcpkg install asio nlohmann-json spdlog
```

#### Homebrew (macOS)
```bash
brew install asio nlohmann-json spdlog
```

#### apt (Ubuntu/Debian)
```bash
sudo apt-get install libasio-dev nlohmann-json3-dev libspdlog-dev
```

**注意**: 使用系统包管理器时，需要修改 `build/CMakeLists.txt` 中的路径配置。

## 目录结构

安装完成后，目录结构应该如下：

```
third_party/
├── README.md              # 本文件
├── install_deps.sh        # 自动安装脚本
├── asio/
│   └── asio/
│       └── include/       # Asio头文件
│           └── asio.hpp
├── json/
│   └── include/           # nlohmann/json头文件
│       └── nlohmann/
│           └── json.hpp
├── spdlog/
│   └── include/           # spdlog头文件
│       └── spdlog/
│           └── spdlog.h
└── http-parser/           # (可选) http-parser源文件
    ├── http_parser.h
    └── http_parser.c
```

## 验证安装

运行以下命令验证依赖是否正确安装：

```bash
cd build
cmake ..
```

如果所有依赖都正确安装，应该看到类似输出：

```
-- Found Asio: /path/to/third_party/asio/asio/include
-- Found nlohmann/json: /path/to/third_party/json/include
-- Found spdlog: /path/to/third_party/spdlog/include
```

## 更新依赖

要更新某个依赖到最新版本：

```bash
cd third_party/<library_name>
git pull
git checkout <latest_tag>
```

## 故障排除

### 问题: CMake找不到依赖

**解决方案**: 确保目录结构正确，或修改 `build/CMakeLists.txt` 中的路径：

```cmake
set(ASIO_INCLUDE_DIR ${THIRD_PARTY_DIR}/asio/asio/include)
set(JSON_INCLUDE_DIR ${THIRD_PARTY_DIR}/json/include)
set(SPDLOG_INCLUDE_DIR ${THIRD_PARTY_DIR}/spdlog/include)
```

### 问题: 编译错误 "asio.hpp not found"

**解决方案**: 
1. 检查Asio是否正确安装
2. 确认路径 `third_party/asio/asio/include/asio.hpp` 存在
3. 重新运行 `cmake ..`

### 问题: Windows上链接错误

**解决方案**: 确保在CMakeLists.txt中定义了 `_WIN32_WINNT`:

```cmake
add_definitions(-D_WIN32_WINNT=0x0601)
```

## 许可证

所有第三方库都有各自的许可证，请查看各库的LICENSE文件。本项目使用这些库遵循其各自的许可证条款。

## 参考链接

- [Asio官方文档](https://think-async.com/Asio/)
- [nlohmann/json文档](https://json.nlohmann.me/)
- [spdlog文档](https://github.com/gabime/spdlog)
- [http-parser](https://github.com/nodejs/http-parser)
