# 文档组织标准

## 📋 标准规则

### 1. 文档位置规则

✅ **正确的做法**:
```
项目根目录/
├── README.md           ← 唯一保留在根目录的 md 文件
├── doc/                ← 所有其他文档都放这里
│   ├── README.md       ← 文档目录索引
│   ├── PROJECT_STATUS.md
│   ├── LOG_CONFIGURATION.md
│   └── ...
├── build/
│   └── README.md       ← 构建相关文档可以在 build/ 目录
└── tests/
    └── EXAMPLES.md     ← 测试相关文档可以在 tests/ 目录
```

❌ **错误的做法**:
```
项目根目录/
├── README.md
├── PROJECT_STATUS.md   ← 不应该在根目录
├── LOG_CONFIG.md       ← 不应该在根目录
└── SOME_DOC.md         ← 不应该在根目录
```

### 2. 文档命名规范

✅ **推荐命名**:
- `PROJECT_STATUS.md` - 使用大写和下划线
- `LOG_CONFIGURATION.md` - 描述性名称
- `BUILD_SYSTEM_SUMMARY.md` - 清晰的主题

❌ **避免命名**:
- `project status.md` - 不要使用空格
- `log-config.md` - 避免使用连字符
- `doc1.md` - 避免无意义的名称

### 3. 文档结构规范

每个文档应包含：

```markdown
# 文档标题

## 概述
简短的说明（1-2 段）

## 主要内容
### 小节 1
内容...

### 小节 2
内容...

## 示例（如适用）
```bash
代码示例
```

## 相关文档
- [其他文档](OTHER_DOC.md)

---
**最后更新**: YYYY-MM-DD
**状态**: ✅ 完成
```

## 📁 目录结构

### 标准目录组织

```
cpp-gateway/
├── README.md                    ← 项目主文档
│
├── doc/                         ← 文档目录
│   ├── README.md                ← 文档索引
│   ├── PROJECT_STATUS.md        ← 项目状态
│   ├── QUICKSTART.md            ← 快速开始
│   ├── STRUCTURE.md             ← 项目结构
│   ├── BUILD_SYSTEM_SUMMARY.md  ← 构建系统
│   ├── BUILD_COMPLETE.md        ← 构建完成报告
│   ├── COMPILE_PROCESS.md       ← 编译过程
│   ├── LDFLAGS_EXPLANATION.md   ← LDFLAGS 说明
│   ├── LOG_CONFIGURATION.md     ← 日志配置
│   ├── README_UPDATE_SUMMARY.md ← 更新记录
│   └── DOCUMENTATION_STANDARD.md ← 本文件
│
├── build/                       ← 构建脚本
│   ├── README.md                ← 构建文档（可以在这里）
│   ├── BUILD_INSTRUCTIONS.md    ← 构建说明（可以在这里）
│   └── ...
│
└── tests/                       ← 测试文件
    ├── EXAMPLES.md              ← 测试示例（可以在这里）
    └── ...
```

## 🎯 文档分类

### 按位置分类

| 位置 | 文档类型 | 示例 |
|------|---------|------|
| 根目录 | 项目主文档 | `README.md` |
| `doc/` | 所有其他文档 | `PROJECT_STATUS.md` |
| `build/` | 构建相关文档 | `build/README.md` |
| `tests/` | 测试相关文档 | `tests/EXAMPLES.md` |

### 按主题分类

| 主题 | 文档 |
|------|------|
| **项目概览** | PROJECT_STATUS.md, QUICKSTART.md, STRUCTURE.md |
| **构建系统** | BUILD_*.md, COMPILE_*.md, LDFLAGS_*.md |
| **配置** | LOG_CONFIGURATION.md, *_CONFIGURATION.md |
| **更新记录** | *_UPDATE_*.md, *_SUMMARY.md |

## 📝 创建新文档的流程

### 步骤 1: 确定文档位置

```bash
# 一般文档 → doc/ 目录
touch doc/NEW_FEATURE.md

# 构建相关 → build/ 目录
touch build/BUILD_GUIDE.md

# 测试相关 → tests/ 目录
touch tests/TEST_GUIDE.md
```

### 步骤 2: 使用标准模板

```markdown
# 新功能说明

## 概述
这个文档说明...

## 详细内容
### 功能 1
...

### 功能 2
...

## 使用示例
```bash
示例代码
```

## 相关文档
- [相关文档](RELATED.md)

---
**创建日期**: 2024-12-06
**最后更新**: 2024-12-06
**状态**: ✅ 完成
```

### 步骤 3: 更新索引

```bash
# 更新 doc/README.md
vim doc/README.md

# 如果需要，更新主 README.md
vim README.md
```

### 步骤 4: 提交到 Git

```bash
git add doc/NEW_FEATURE.md doc/README.md
git commit -m "docs: 添加新功能说明文档"
```

## 🔍 文档查找

### 快速查找

```bash
# 列出所有文档
ls doc/

# 搜索文档内容
grep -r "关键词" doc/

# 查看文档索引
cat doc/README.md
```

### 按主题查找

```bash
# 构建相关
ls doc/BUILD*.md doc/COMPILE*.md

# 配置相关
ls doc/*CONFIGURATION*.md

# 项目信息
ls doc/PROJECT*.md doc/STRUCTURE.md
```

## ✅ 检查清单

创建或移动文档时，确保：

- [ ] 文档放在正确的目录（doc/、build/ 或 tests/）
- [ ] 使用大写字母和下划线命名
- [ ] 包含标准的文档结构
- [ ] 更新 doc/README.md 索引
- [ ] 如需要，更新主 README.md
- [ ] 添加最后更新日期
- [ ] 提交到 Git

## 🎓 最佳实践

### 1. 保持根目录整洁

- 只保留 README.md 在根目录
- 所有其他文档移到 doc/

### 2. 使用描述性名称

- ✅ `LOG_CONFIGURATION.md`
- ❌ `config.md`

### 3. 保持文档更新

- 功能变更时更新相关文档
- 定期检查文档准确性
- 标注最后更新日期

### 4. 交叉引用

- 在文档中链接相关文档
- 在 README.md 中链接重要文档
- 在 doc/README.md 中维护完整索引

### 5. 使用一致的格式

- 统一的标题层级
- 统一的代码块格式
- 统一的列表格式

## 📊 当前文档统计

### 文档分布

| 位置 | 数量 | 文档 |
|------|------|------|
| 根目录 | 1 | README.md |
| doc/ | 10 | 各类文档 |
| build/ | 5 | 构建相关 |
| tests/ | 1 | 测试示例 |

### 文档类型

| 类型 | 数量 |
|------|------|
| 项目概览 | 3 |
| 构建系统 | 4 |
| 配置说明 | 1 |
| 更新记录 | 1 |
| 标准规范 | 1 |

## 🔄 维护流程

### 定期维护

1. **每月检查**
   - 检查文档准确性
   - 更新过时信息
   - 添加新功能文档

2. **版本发布时**
   - 更新 PROJECT_STATUS.md
   - 更新 README.md
   - 检查所有文档链接

3. **重大变更时**
   - 创建新文档说明变更
   - 更新相关文档
   - 在 README.md 中突出显示

## 🎉 总结

遵循这个标准，可以：

- ✅ 保持项目根目录整洁
- ✅ 文档组织清晰
- ✅ 易于查找和维护
- ✅ 提高项目专业性

**核心原则**: 根目录只保留 README.md，其他文档都放在 doc/ 目录下。

---

**创建日期**: 2024-12-06  
**最后更新**: 2024-12-06  
**状态**: ✅ 标准已确立
