# 第三方依赖

本项目使用以下第三方库：

## 1. Asio (standalone)
- 版本: 1.28.0+
- 用途: 跨平台异步I/O
- 获取方式: 
  ```bash
  git clone https://github.com/chriskohlhoff/asio.git
  cd asio/asio
  ```
- 或下载: https://think-async.com/Asio/

## 2. nlohmann/json
- 版本: 3.11.0+
- 用途: JSON解析
- 获取方式:
  ```bash
  git clone https://github.com/nlohmann/json.git
  ```
- 或下载单头文件: https://github.com/nlohmann/json/releases

## 3. spdlog
- 版本: 1.12.0+
- 用途: 日志库
- 获取方式:
  ```bash
  git clone https://github.com/gabime/spdlog.git
  ```

## 4. Google Test
- 版本: 1.14.0+
- 用途: 单元测试框架
- 获取方式:
  ```bash
  git clone https://github.com/google/googletest.git
  ```

## 5. RapidCheck
- 版本: latest
- 用途: 属性测试框架
- 获取方式:
  ```bash
  git clone https://github.com/emil-e/rapidcheck.git
  ```

## 快速安装脚本

```bash
cd third_party

# Asio
git clone https://github.com/chriskohlhoff/asio.git

# nlohmann/json
git clone https://github.com/nlohmann/json.git

# spdlog
git clone https://github.com/gabime/spdlog.git

# Google Test
git clone https://github.com/google/googletest.git

# RapidCheck
git clone https://github.com/emil-e/rapidcheck.git
```

注意：这些库都是header-only或可以作为header-only使用，简化了集成过程。
