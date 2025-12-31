---
description: Python 代码格式化和检查
argument-hint: [--check | --staged]
allowed-tools: Bash
---

# /lint 命令

运行 Python 代码格式化和检查工具。

## 执行流程

### 默认模式（格式化）

```bash
# 格式化代码
black examples/ --line-length 100

# 排序导入
isort examples/
```

### --check 模式（只检查）

```bash
# 检查格式
black examples/ --check --line-length 100

# 检查导入排序
isort examples/ --check
```

### --staged 模式（只处理暂存文件）

```bash
# 获取暂存的 Python 文件
git diff --cached --name-only --diff-filter=ACM | grep '\.py$'

# 对这些文件运行格式化
```

## 输出格式

```
✅ 代码检查完成

**Black**: [通过 | 修复 N 个文件]
**isort**: [通过 | 修复 N 个文件]

提示: 运行 `git diff` 查看修改
```

或检查模式：

```
❌ 代码检查失败

**Black**: N 个文件需要格式化
**isort**: N 个文件导入需要排序

运行 `/lint` 自动修复
```

## 使用示例

```
/lint           # 格式化代码
/lint --check   # 只检查，不修改
/lint --staged  # 只处理暂存文件
```

## 前置条件

确保已安装工具：

```bash
pip install black isort
```

## 配置

项目配置在 `pyproject.toml`:

```toml
[tool.black]
line-length = 100

[tool.isort]
profile = "black"
line_length = 100
```
