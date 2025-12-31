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
pip install -e ".[dev]"

# 或手动安装
pip install black isort pytest mypy flake8 bandit
```

---

## 代码风格

### Pre-commit (推荐)

```bash
# 安装 pre-commit
pip install pre-commit

# 激活 hooks
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

### 格式化工具

```bash
# 格式化代码
black examples/ paddleocr_guide/ tests/ --line-length 100

# 排序导入
isort examples/ paddleocr_guide/ tests/
```

### 检查（不修改）

```bash
black examples/ --check
isort examples/ --check
flake8 examples/
mypy examples/
```

### 配置

项目已在 `pyproject.toml` 中配置：

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 100
```

---

## CLI 工具开发

### 目录结构

```
paddleocr_guide/
├── __init__.py      # 版本信息
└── cli.py           # 命令行入口
```

### 添加新命令

```python
# 在 cli.py 中添加
@cli.command()
@click.argument("input")
@click.option("--output", "-o", help="输出路径")
def new_command(input: str, output: str):
    """命令说明"""
    # 实现逻辑
    pass
```

### 测试命令

```bash
# 安装开发模式
pip install -e .

# 测试命令
paddleocr-guide --help
paddleocr-guide new_command input.png
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

## 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_common.py -v

# 生成覆盖率报告
pytest tests/ --cov=examples --cov-report=html
```

### 测试结构

```
tests/
├── conftest.py        # pytest fixtures
├── test_common.py     # 公共模块测试 (27个用例)
└── test_basic_ocr.py  # OCR 测试 (15个用例，已跳过)
```

> ⚠️ **注意**: OCR 相关测试已跳过，因为 PaddleOCR 3.x 存在内存问题

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

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/ci.yml
- lint: black, isort, flake8
- type-check: mypy
- test: pytest (Ubuntu/macOS, Python 3.8-3.12)
- security: bandit
```

### 本地运行 CI 检查

```bash
# 格式检查
black --check .
isort --check .

# 类型检查
mypy examples/

# 安全检查
bandit -r examples/ -ll
```

---

## 发布流程

1. 更新版本号（pyproject.toml, paddleocr_guide/__init__.py）
2. 更新 CHANGELOG.md
3. 运行测试: `pytest tests/`
4. 格式化代码: `pre-commit run --all-files`
5. 创建 Git tag: `git tag v0.2.1`
6. 推送到 GitHub: `git push && git push --tags`
