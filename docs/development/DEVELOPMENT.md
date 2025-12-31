# 开发规范

本文档定义项目开发规范和约定。

---

## 环境配置

### Python 版本

- 最低要求: Python 3.8
- 推荐版本: Python 3.10+

### 安装依赖

```bash
# 基础依赖
pip install paddleocr

# 开发依赖
pip install black isort pytest
```

---

## 代码风格

### 格式化工具

```bash
# 格式化代码
black examples/ --line-length 100

# 排序导入
isort examples/
```

### 检查（不修改）

```bash
black examples/ --check
isort examples/ --check
```

### 配置

项目已在 `pyproject.toml` 中配置：

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 100
```

---

## Git 规范

### 分支命名

- `main`: 主分支
- `feature/xxx`: 新功能
- `fix/xxx`: Bug 修复
- `docs/xxx`: 文档更新

### 提交信息

格式: `<type>: <description>`

类型:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响逻辑）
- `refactor`: 重构
- `test`: 测试
- `chore`: 杂项

示例:
```
feat: add batch OCR example
fix: handle empty image path
docs: update macOS troubleshooting
```

---

## 文档规范

### 语言

- 代码注释: 中英双语
- 用户文档: 中文优先，提供英文版
- 开发文档: 中文

### Markdown

- 使用中文标点
- 代码块标明语言
- 表格对齐

---

## 测试

### 运行示例

```bash
# 运行单个示例
python examples/basic/01_simple_ocr.py

# 确保测试图片存在
ls assets/test_images/
```

### 单元测试（待实现）

```bash
pytest tests/
```

---

## AI 协作

### Slash Commands

| 命令 | 用途 |
|------|------|
| `/start` | 恢复项目记忆 |
| `/checkpoint` | 阶段性保存 |
| `/end` | 每日结束 |
| `/weekly` | 每周维护 |
| `/lint` | Python 代码检查 |

### Token 预算

- CONTEXT.md: < 1500 tokens
- CURRENT.md: < 1000 tokens
- /start 总读取: < 3000 tokens

---

## 发布流程

1. 更新版本号（pyproject.toml）
2. 更新 CHANGELOG
3. 创建 Git tag
4. 推送到 GitHub
