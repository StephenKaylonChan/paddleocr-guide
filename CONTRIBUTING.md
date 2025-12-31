# 贡献指南 | Contributing Guide

感谢您对 PaddleOCR Guide 项目的关注！我们欢迎任何形式的贡献。

Thank you for your interest in the PaddleOCR Guide project! We welcome contributions of all kinds.

---

## 目录 | Table of Contents

- [行为准则](#行为准则--code-of-conduct)
- [如何贡献](#如何贡献--how-to-contribute)
- [开发环境设置](#开发环境设置--development-setup)
- [代码规范](#代码规范--code-style)
- [提交规范](#提交规范--commit-guidelines)
- [Pull Request 流程](#pull-request-流程--pr-process)

---

## 行为准则 | Code of Conduct

本项目采用 [贡献者公约](https://www.contributor-covenant.org/zh-cn/version/2/0/code_of_conduct/) 作为行为准则。
参与项目即表示您同意遵守该准则。

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)
code of conduct. By participating, you agree to uphold this code.

---

## 如何贡献 | How to Contribute

### 报告问题 | Reporting Issues

1. 在 [Issues](https://github.com/stephenkaylonchan/paddleocr-guide/issues) 页面搜索是否已有类似问题
2. 如果没有，创建新 Issue 并提供：
   - 清晰的问题描述
   - 复现步骤
   - 预期行为与实际行为
   - 运行环境信息 (Python 版本、操作系统等)
   - 相关代码片段或错误日志

### 提交代码 | Submitting Code

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 进行修改并编写测试
4. 确保通过所有检查 (见下文)
5. 提交 Pull Request

### 改进文档 | Improving Documentation

- 修正错别字或翻译错误
- 改进示例说明
- 添加缺失的文档
- 翻译文档到其他语言

---

## 开发环境设置 | Development Setup

### 1. 克隆仓库

```bash
git clone https://github.com/stephenkaylonchan/paddleocr-guide.git
cd paddleocr-guide
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 或使用 conda
conda create -n paddleocr-guide python=3.11
conda activate paddleocr-guide
```

### 3. 安装依赖

```bash
# 安装核心依赖
pip install paddlepaddle paddleocr

# 安装开发依赖
pip install -e ".[dev]"
```

### 4. 验证安装

```bash
# 运行测试
pytest tests/ -v

# 检查导入
python -c "from examples._common import OCRException; print('OK')"
```

---

## 代码规范 | Code Style

本项目遵循以下代码规范：

### Python 代码

- **格式化**: 使用 [Black](https://black.readthedocs.io/) (行长 100)
- **导入排序**: 使用 [isort](https://pycqa.github.io/isort/) (profile=black)
- **Lint**: 使用 [Flake8](https://flake8.pycqa.org/)
- **类型检查**: 使用 [mypy](https://mypy.readthedocs.io/)

### 运行代码检查

```bash
# 格式化代码
black examples/ tests/ --line-length 100
isort examples/ tests/ --profile black

# 检查格式（不修改）
black --check examples/ tests/
isort --check-only examples/ tests/

# Lint 检查
flake8 examples/ tests/ --max-line-length=100 --ignore=E501,W503

# 类型检查
mypy examples/ --ignore-missing-imports

# 安全检查
bandit -r examples/ -ll
```

### 代码模板

所有示例文件应遵循统一模板：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[功能名称] - [功能描述]
[English Title] - [English Description]

适用模型: [模型名称]
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Union

from examples._common import (
    OCRException,
    setup_logging,
    get_logger,
)

logger = get_logger(__name__)


def main() -> None:
    """主函数"""
    setup_logging()
    # 实现逻辑


if __name__ == "__main__":
    main()
```

### 文档字符串规范

使用 Google 风格的 docstring：

```python
def process_image(
    image_path: Union[str, Path],
    *,
    lang: str = "ch",
    output_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """
    处理单张图片

    该函数使用 PaddleOCR 识别图片中的文字。

    Args:
        image_path: 图片路径
        lang: 语言代码，默认 'ch'
        output_dir: 输出目录（可选）

    Returns:
        dict[str, Any]: 识别结果
            - texts: list[str] - 识别的文本列表
            - confidence: float - 平均置信度

    Raises:
        OCRFileNotFoundError: 图片不存在时
        OCRProcessError: 识别失败时

    Example:
        >>> result = process_image("test.png", lang="ch")
        >>> print(result["texts"])
    """
```

---

## 提交规范 | Commit Guidelines

### 提交信息格式

使用约定式提交 (Conventional Commits)：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 类型 (type)

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```bash
# 新功能
git commit -m "feat(advanced): 添加印章识别示例"

# Bug 修复
git commit -m "fix(common): 修复日志配置路径问题"

# 文档更新
git commit -m "docs: 更新 README 安装说明"

# 代码重构
git commit -m "refactor(basic): 统一使用上下文管理器"
```

---

## Pull Request 流程 | PR Process

### 1. 创建 PR 前

- [ ] 确保代码通过所有检查
- [ ] 编写或更新相关测试
- [ ] 更新相关文档
- [ ] 更新 CHANGELOG.md (如适用)

### 2. PR 标题格式

遵循提交信息格式：

```
feat(basic): 添加 PDF 批量处理功能
```

### 3. PR 描述模板

```markdown
## 描述 | Description

简要描述此 PR 的更改内容。

## 更改类型 | Type of Change

- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 相关 Issue

Fixes #123

## 测试 | Testing

描述如何测试这些更改。

## 检查清单 | Checklist

- [ ] 代码符合项目规范
- [ ] 已添加/更新测试
- [ ] 已更新相关文档
- [ ] 所有检查通过
```

### 4. 代码审查

- 所有 PR 需要至少一位维护者审查
- 请及时响应审查意见
- 审查通过后由维护者合并

---

## 联系方式 | Contact

如有任何问题，请通过以下方式联系：

- **GitHub Issues**: [提交问题](https://github.com/stephenkaylonchan/paddleocr-guide/issues)
- **Discussions**: [参与讨论](https://github.com/stephenkaylonchan/paddleocr-guide/discussions)

---

感谢您的贡献！
Thank you for contributing!
