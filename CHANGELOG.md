# 变更日志 | Changelog

本文件记录了项目的所有重要变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.1] - 2025-12-31

### 新增 | Added

#### CLI 命令行工具
- 新增 `paddleocr_guide/` 模块
- 新增 5 个 CLI 命令：
  - `paddleocr-guide scan` - 识别单张图片
  - `paddleocr-guide batch` - 批量处理目录
  - `paddleocr-guide pdf` - PDF 转 Markdown
  - `paddleocr-guide langs` - 查看支持的语言
  - `paddleocr-guide info` - 查看环境信息
- CLI 内置图片大小检查（限制 10MB / 1600万像素）

#### 代码质量
- 新增 `.pre-commit-config.yaml` (black, isort, pre-commit-hooks)
- README 添加 CI/pre-commit/black 徽章

### 修复 | Fixed
- 修复 Python 3.12 动态导入 dataclass 兼容性问题
- 修复 `format_ocr_result` 处理 None 输入
- 修复 `normalize_language` 大小写敏感问题

### 文档 | Documentation
- 记录 PaddleOCR 内存占用过高问题 (macOS ARM 40GB+)
- 更新 troubleshooting.md 添加内存问题解决方案
- 更新所有 README 添加 CLI 和内存警告

---

## [0.2.0] - 2025-12-31

### 新增 | Added

#### 公共模块 (_common/)
- 新增 `examples/_common/` 公共模块，包含 6 个核心文件：
  - `__init__.py` - 统一导出接口
  - `exceptions.py` - 自定义异常层次结构 (OCRException 及其子类)
  - `config.py` - 路径配置和常量定义
  - `logging_config.py` - 日志系统配置
  - `utils.py` - 通用工具函数
  - `base.py` - 基础类和上下文管理器

#### 基础示例 (basic/)
- 完全重写 3 个基础示例：
  - `01_simple_ocr.py` - 简单 OCR 识别
  - `02_batch_ocr.py` - 批量图片处理
  - `03_multilingual.py` - 多语言识别

#### 文档处理示例 (document/)
- 完全重写 3 个文档处理示例：
  - `01_pdf_to_markdown.py` - PDF/图片转 Markdown
  - `02_table_recognition.py` - 表格识别和导出
  - `03_layout_analysis.py` - 版面分析

#### 高级示例 (advanced/)
- 完全重写 10 个高级示例：
  - `01_seal_recognition.py` - 印章识别
  - `02_formula_recognition.py` - 数学公式识别 (→ LaTeX)
  - `03_chart_recognition.py` - 图表识别
  - `04_chatocr_extraction.py` - 智能信息抽取
  - `05_handwriting_ocr.py` - 手写文字识别
  - `06_vertical_text.py` - 竖排文字识别
  - `07_doc_preprocessing.py` - 文档预处理/矫正
  - `08_paddleocr_vl.py` - 视觉语言模型
  - `09_doc_translation.py` - 文档翻译
  - `10_doc_understanding.py` - 文档理解

#### 测试框架
- 新增 `tests/` 目录和测试框架：
  - `conftest.py` - pytest fixtures
  - `test_common.py` - 公共模块测试
  - `test_basic_ocr.py` - 基础 OCR 测试

#### CI/CD
- 新增 GitHub Actions CI/CD 配置 (`.github/workflows/ci.yml`)
  - 代码格式检查 (black, isort, flake8)
  - 类型检查 (mypy)
  - 单元测试 (pytest)
  - 安全检查 (bandit)

#### 文档
- 新增 `CHANGELOG.md` - 变更日志
- 新增 `CONTRIBUTING.md` - 贡献指南

### 改进 | Improved

#### 代码质量
- 所有示例统一使用上下文管理器模式 (`with` 语句)
- 添加完整的类型提示 (Type Hints)
- 使用 dataclass 封装结果对象
- 统一的异常处理机制
- 使用 logging 替代 print()

#### 文档
- 所有示例添加详细的中英双语文档字符串
- 添加使用示例和参数说明
- 添加平台兼容性说明 (macOS ARM 限制)

#### 项目配置
- 更新 `pyproject.toml` 版本至 0.2.0
- 修复 setuptools 包查找配置
- 添加完整的工具配置 (pytest, mypy, black, isort, ruff, bandit)

### 修复 | Fixed
- 修复 `pyproject.toml` 中 `[tool.setuptools.packages.find]` 的 `where` 配置
- 修复作者信息

### 变更 | Changed
- API 调整：所有 `ocr()` 方法改为 `predict()`，符合 PaddleOCR 3.x 规范
- 移除废弃参数：`use_angle_cls`, `show_log` 等

---

## [0.1.0] - 2024-12-30

### 新增 | Added
- 初始版本发布
- 16 个 PaddleOCR 3.x 示例
- 基础 README 文档
- MIT 许可证

---

## 版本对比 | Version Comparison

| 版本 | 代码质量 | 错误处理 | 类型提示 | 文档完整度 | CI/CD |
|------|---------|---------|---------|-----------|-------|
| 0.1.0 | 6.7/10 | 基础 | 部分 | 中文 | 无 |
| 0.2.0 | 9/10 | 完整 | 100% | 中英双语 | 完整 |

---

## 贡献者 | Contributors

- Stephen Chan (@stephenkaylonchan) - 项目维护者

---

## 链接 | Links

- [项目主页](https://github.com/stephenkaylonchan/paddleocr-guide)
- [问题反馈](https://github.com/stephenkaylonchan/paddleocr-guide/issues)
- [PaddleOCR 官方](https://github.com/PaddlePaddle/PaddleOCR)
