# 快速开始指南

5分钟快速上手C++ Gateway项目。

## 1. 安装依赖 (2分钟)

```bash
# 克隆项目后，安装第三方依赖
./third_party/install_deps.sh
```

这会自动安装：
- Asio (异步网络库)
- nlohmann/json (JSON解析)
- spdlog (日志库)

## 2. 编译项目 (1分钟)

```bash
cd build
cmake ..
make
```

编译成功后，可执行文件位于 `output/gateway`。

## 3. 配置网关 (1分钟)

编辑 `config/config.json`：

```json
{
  "listen_port": 8080,
  "log_level": "info",
  "log_file": "log/gateway.log",
  "backend_timeout_ms": 5000,
  "routes": [
    {
      "path_pattern": "/api",
      "match_type": "prefix",
      "priority": 1,
      "backends": [
        "http://localhost:9001"
      ]
    }
  ]
}
```

## 4. 启动测试后端 (30秒)

```bash
# 在新终端启动测试后端
python3 tests/test_backend.py 9001
```

## 5. 运行网关 (30秒)

```bash
# 在另一个终端启动网关
./output/gateway config/config.json
```

## 6. 测试 (30秒)

```bash
# 发送测试请求
curl http://localhost:8080/api/test

# 应该看到来自后端的响应
```

## 完整测试流程

```bash
# 1. 安装依赖
./third_party/install_deps.sh

# 2. 编译
cd build && cmake .. && make && cd ..

# 3. 启动后端（后台运行）
python3 tests/test_backend.py 9001 &
python3 tests/test_backend.py 9002 &

# 4. 启动网关（后台运行）
./output/gateway config/config.json &

# 5. 运行测试脚本
./tests/test_gateway.sh

# 6. 查看日志
tail -f log/gateway.log
```

## 故障排除

### 问题: 找不到依赖库

```bash
# 重新安装依赖
cd third_party
rm -rf asio json spdlog
cd ..
./third_party/install_deps.sh
```

### 问题: 端口被占用

修改 `config/config.json` 中的 `listen_port`。

### 问题: 后端连接失败

确保后端服务正在运行：
```bash
curl http://localhost:9001
```

## 下一步

- 阅读完整文档: `README.md`
- 查看迁移指南: `doc/MIGRATION_GUIDE.md`
- 了解第三方库: `third_party/README.md`
- 运行更多测试: `tests/EXAMPLES.md`

---

**需要帮助?** 查看 `build/README.md` 获取详细的构建说明。
