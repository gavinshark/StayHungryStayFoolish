# 测试文件组织

## ✅ 完成的工作

已将所有测试相关的文件移动到 `tests/` 目录，并建立了测试组织标准。

## 📁 文件移动

### 移动的文件

- `test_simple.sh` → `tests/test_simple.sh`

### 已在 tests/ 目录的文件

- `test_gateway.sh` - 网关功能测试
- `test_backend.py` - 测试后端服务器
- `test_log.sh` - 日志功能测试
- `EXAMPLES.md` - 使用示例文档
- `README.md` - 测试目录说明（新建）

## 📊 当前目录结构

```
cpp-gateway/
├── tests/                      ← 所有测试文件
│   ├── README.md               ← 测试目录说明
│   ├── EXAMPLES.md             ← 使用示例
│   ├── test_gateway.sh         ← 网关测试
│   ├── test_simple.sh          ← 简单测试
│   ├── test_log.sh             ← 日志测试
│   └── test_backend.py         ← 测试后端
│
├── log/                        ← 日志输出目录
│   └── gateway.log
│
├── output/                     ← 编译输出目录
│   ├── obj/
│   └── gateway
│
└── ...
```

## 🎯 组织标准

### 规则

1. **所有测试文件都放在 tests/ 目录**
2. **测试脚本命名**: `test_*.sh`
3. **测试后端命名**: `test_*.py`
4. **测试文档**: 大写 `.md` 文件

### 文件类型

| 类型 | 位置 | 命名规范 | 示例 |
|------|------|---------|------|
| 测试脚本 | `tests/` | `test_*.sh` | `test_gateway.sh` |
| 测试后端 | `tests/` | `test_*.py` | `test_backend.py` |
| 测试文档 | `tests/` | `*.md` | `EXAMPLES.md` |
| 日志文件 | `log/` | `*.log` | `gateway.log` |

## 🚀 使用方法

### 运行测试

```bash
# 完整测试
./tests/test_gateway.sh

# 简单测试
./tests/test_simple.sh

# 日志测试
./tests/test_log.sh
```

### 查看测试文档

```bash
# 测试目录说明
cat tests/README.md

# 使用示例
cat tests/EXAMPLES.md
```

## 📝 添加新测试

### 步骤

1. **创建测试脚本**
   ```bash
   vim tests/test_new_feature.sh
   ```

2. **添加执行权限**
   ```bash
   chmod +x tests/test_new_feature.sh
   ```

3. **更新文档**
   ```bash
   vim tests/README.md
   ```

4. **运行测试**
   ```bash
   ./tests/test_new_feature.sh
   ```

### 模板

```bash
#!/bin/bash
# 测试新功能

echo "=== 测试新功能 ==="
echo ""

# 1. 准备
echo "1. 准备测试环境..."
# ...

# 2. 执行测试
echo "2. 执行测试..."
# ...

# 3. 验证结果
echo "3. 验证结果..."
# ...

# 4. 清理
echo "4. 清理..."
# ...

echo ""
echo "=== 测试完成 ==="
```

## 🔍 测试文件说明

### test_gateway.sh

**用途**: 完整的网关功能测试

**测试内容**:
- 路由匹配（精确、前缀）
- 负载均衡（轮询）
- 错误处理（404, 503）
- POST 请求

**运行**:
```bash
./tests/test_gateway.sh
```

### test_simple.sh

**用途**: 快速测试基本功能

**测试内容**:
- 后端连接
- 基本请求转发
- 端口监听

**运行**:
```bash
./tests/test_simple.sh
```

### test_log.sh

**用途**: 测试日志功能

**测试内容**:
- 日志目录创建
- 日志文件写入
- 日志级别

**运行**:
```bash
./tests/test_log.sh
```

### test_backend.py

**用途**: 模拟后端服务器

**功能**:
- 接收 HTTP 请求
- 返回 JSON 响应
- 显示请求信息

**运行**:
```bash
python3 tests/test_backend.py <port>
```

## 📊 测试统计

| 类型 | 数量 | 文件 |
|------|------|------|
| 测试脚本 | 3 | test_gateway.sh, test_simple.sh, test_log.sh |
| 测试后端 | 1 | test_backend.py |
| 测试文档 | 2 | README.md, EXAMPLES.md |
| **总计** | **6** | |

## ✨ 优势

### 1. 组织清晰

- ✅ 所有测试文件集中在一个目录
- ✅ 易于查找和管理
- ✅ 避免根目录混乱

### 2. 命名规范

- ✅ 统一的命名前缀 `test_*`
- ✅ 描述性的文件名
- ✅ 易于识别

### 3. 文档完整

- ✅ README.md 说明测试目录
- ✅ EXAMPLES.md 提供使用示例
- ✅ 每个测试都有说明

### 4. 易于维护

- ✅ 新测试添加到 tests/ 目录
- ✅ 统一的组织标准
- ✅ 清晰的文档

## 🎓 最佳实践

### 1. 保持测试独立

每个测试脚本应该：
- 独立运行
- 自己准备环境
- 自己清理资源

### 2. 提供清晰输出

测试脚本应该：
- 显示测试步骤
- 显示测试结果
- 显示错误信息

### 3. 处理错误

测试脚本应该：
- 检查前置条件
- 处理失败情况
- 返回正确的退出码

### 4. 文档化

每个测试应该：
- 在 README.md 中说明
- 提供使用示例
- 说明预期结果

## 🔄 维护流程

### 定期检查

1. 确保所有测试可运行
2. 更新过时的测试
3. 添加新功能的测试

### 版本发布

1. 运行所有测试
2. 确保测试通过
3. 更新测试文档

## 🎉 总结

✅ **测试文件组织完成**

- 所有测试文件移动到 tests/ 目录
- 建立了测试组织标准
- 创建了完整的测试文档
- 提供了清晰的使用指南

**标准已确立**: 以后所有测试相关的文件都应放在 tests/ 目录下。

---

**完成日期**: 2024-12-06  
**测试文件数量**: 6  
**状态**: ✅ 完成
