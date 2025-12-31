# PaddleOCR 实战指南

> 基于 PaddleOCR 3.0 的中文 OCR 解决方案，专为 macOS 用户优化

[![CI](https://github.com/StephenKaylonChan/paddleocr-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/StephenKaylonChan/paddleocr-guide/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.x-green.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[English](README_en.md) | **中文**

**GitHub**: [stephenkaylonchan/paddleocr-guide](https://github.com/stephenkaylonchan/paddleocr-guide)

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [CLI 命令行工具](#cli-命令行工具)
- [模型选择指南](#模型选择指南)
- [使用示例](#使用示例)
- [macOS 用户须知](#macos-用户须知)
- [常见问题](#常见问题)
- [项目结构](#项目结构)
- [贡献指南](#贡献指南)

---

## 项目简介

本项目提供 PaddleOCR 3.0 的实战示例和最佳实践，帮助开发者快速上手中文 OCR（光学字符识别）。

**为什么选择 PaddleOCR？**

- 超轻量级模型（PP-OCRv5 仅 4.1MB）
- 80+ 种语言支持
- 开箱即用，无需训练
- 支持文档解析、表格识别、信息抽取

---

## 功能特性

| 功能 | 描述 | 示例 |
|------|------|------|
| **基础示例** | | |
| 基础 OCR | 图片文字识别 | [01_simple_ocr.py](examples/basic/01_simple_ocr.py) |
| 批量处理 | 多图片批量识别 | [02_batch_ocr.py](examples/basic/02_batch_ocr.py) |
| 多语言 | 中英日韩等语言 | [03_multilingual.py](examples/basic/03_multilingual.py) |
| **文档处理** | | |
| 表格识别 | 识别并导出表格 | [02_table_recognition.py](examples/document/02_table_recognition.py) |
| PDF 转换 | PDF 转 Markdown | [01_pdf_to_markdown.py](examples/document/01_pdf_to_markdown.py) |
| 版面分析 | 文档结构分析 | [03_layout_analysis.py](examples/document/03_layout_analysis.py) |
| **高级功能** | | |
| 印章识别 | 公章/印章检测提取 | [01_seal_recognition.py](examples/advanced/01_seal_recognition.py) |
| 公式识别 | 数学公式转 LaTeX | [02_formula_recognition.py](examples/advanced/02_formula_recognition.py) |
| 图表识别 | 图表内容理解 | [03_chart_recognition.py](examples/advanced/03_chart_recognition.py) |
| 智能抽取 | 票据/证件信息提取 | [04_chatocr_extraction.py](examples/advanced/04_chatocr_extraction.py) |
| 手写识别 | 手写文字识别 | [05_handwriting_ocr.py](examples/advanced/05_handwriting_ocr.py) |
| 竖排文字 | 竖排/纵向文字 | [06_vertical_text.py](examples/advanced/06_vertical_text.py) |
| 文档预处理 | 方向/弯曲矫正 | [07_doc_preprocessing.py](examples/advanced/07_doc_preprocessing.py) |
| 视觉语言 | VL 模型 (非ARM) | [08_paddleocr_vl.py](examples/advanced/08_paddleocr_vl.py) |
| 文档翻译 | 多语言翻译 | [09_doc_translation.py](examples/advanced/09_doc_translation.py) |
| 文档理解 | 文档问答 | [10_doc_understanding.py](examples/advanced/10_doc_understanding.py) |

---

## 快速开始

### 环境要求

- Python 3.8+
- macOS / Linux / Windows

### 安装

```bash
# 基础安装
pip install paddleocr

# 完整安装（推荐）
pip install "paddleocr[all]"
```

### 验证安装

```bash
python -c "from paddleocr import PaddleOCR; print('安装成功')"
```

### 第一个 OCR 程序

```python
from paddleocr import PaddleOCR

# 初始化（首次运行会自动下载模型）
ocr = PaddleOCR(lang='ch')

# 识别图片 (PaddleOCR 3.x API)
result = ocr.predict('your_image.png')

# 输出结果
for res in result:
    res.print()  # 直接打印结果
    # 或获取 JSON 格式
    # print(res.json)
```

---

## CLI 命令行工具

安装后可直接在终端使用，无需编写代码：

```bash
# 安装
pip install -e .

# 查看帮助
paddleocr-guide --help
```

### 可用命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `scan` | 识别单张图片 | `paddleocr-guide scan photo.png` |
| `batch` | 批量处理目录 | `paddleocr-guide batch ./images/` |
| `pdf` | PDF 转 Markdown | `paddleocr-guide pdf doc.pdf -o out.md` |
| `langs` | 查看支持的语言 | `paddleocr-guide langs` |
| `info` | 查看环境信息 | `paddleocr-guide info` |

### 常用选项

```bash
# 指定语言
paddleocr-guide scan image.png --lang en

# 输出到文件
paddleocr-guide scan image.png -o result.txt

# 输出 JSON 格式
paddleocr-guide scan image.png --json
```

> **注意**: CLI 内置图片大小检查，超过 10MB 或 1600 万像素的图片会被拒绝，使用 `--force` 强制处理。

---

## 模型选择指南

PaddleOCR 3.0 提供四大核心模型：

| 模型 | 用途 | macOS ARM | 模型大小 | 适用场景 |
|------|------|-----------|---------|---------|
| **PP-OCRv5** | 传统 OCR | ✅ 完全支持 | ~10MB | 通用文字识别 |
| **PP-StructureV3** | 文档解析 | ✅ 完全支持 | ~50MB | 表格/PDF/版面分析 |
| **PP-ChatOCRv4** | 智能抽取 | ✅ 完全支持 | - | 票据/证件信息提取 |
| **PaddleOCR-VL** | 视觉语言 | ❌ 不支持 | ~900MB | 109种语言/复杂文档 |

### 如何选择？

```
你的使用场景是？
│
├─ 简单文字识别 → PP-OCRv5 ✅
│
├─ 复杂文档/表格/PDF → PP-StructureV3 ✅
│
├─ 票据/证件信息抽取 → PP-ChatOCRv4 ✅
│
└─ 109种语言 / 需要视觉理解
   ├─ 有 x86/GPU → PaddleOCR-VL ✅
   └─ macOS ARM → PP-OCRv5 (功能受限) ⚠️
```

📖 详细对比：[模型选择指南](docs/zh/model_comparison.md)

📖 完整 API：[API 参考文档](docs/zh/api_reference.md)

---

## 使用示例

### 基础 OCR (PaddleOCR 3.x)

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch')
result = ocr.predict('image.png')

for res in result:
    res.print()
```

### 表格识别 (PPStructureV3)

```python
from paddleocr import PPStructureV3

pipeline = PPStructureV3(use_table_recognition=True)
result = pipeline.predict(input='table.png')

for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')
```

### 智能信息抽取 (PPChatOCRv4Doc)

```python
from paddleocr import PPChatOCRv4Doc

chat_ocr = PPChatOCRv4Doc(use_seal_recognition=True)
result = chat_ocr.predict(
    input='invoice.png',
    prompt='提取发票号码、金额、日期'
)

for res in result:
    res.print()
```

📖 更多示例：[examples/](examples/)

---

## macOS 用户须知

### 重要限制

> ⚠️ **PaddleOCR-VL 不支持 Apple Silicon (M1/M2/M3/M4)**

如果你使用的是 M 系列芯片的 Mac，请使用 **PP-OCRv5** 替代。

### 已知问题：内存占用过高

> ⚠️ **PaddleOCR 3.x 在 macOS ARM 上可能占用大量内存（40GB+），可能导致系统卡死**

**临时解决方案**：
```python
# 禁用预处理模型减少内存占用
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
```

详见 [常见问题解决](docs/zh/troubleshooting.md#q5-内存不足-oom--系统卡死)

### 推荐方案

| 场景 | 推荐模型 | 说明 |
|------|---------|------|
| 通用文字识别 | PP-OCRv5 | 完全兼容，功能完整 |
| 文档解析 | PP-StructureV3 | 完全兼容 |
| 信息抽取 | PP-ChatOCRv4 | 需配置 ERNIE API |
| 多语言识别 | PP-OCRv5 | 支持中英日韩等 |

### 常见错误及解决

#### 1. `illegal instruction` 错误

```bash
# 原因：安装了 x86 版本的包
# 解决：重新安装原生 ARM 版本
pip uninstall paddlepaddle paddleocr
pip install paddlepaddle paddleocr
```

#### 2. `libiomp5.dylib` 冲突

```python
# 在代码开头添加
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

#### 3. 无 GPU 加速

macOS 不支持 CUDA，PaddlePaddle 也暂不支持 Apple MPS。所有推理在 CPU 上运行。

📖 更多问题：[常见问题解决](docs/zh/troubleshooting.md)

---

## 常见问题

### Q: 首次运行很慢？

A: 首次运行会自动下载模型（约 10MB），请耐心等待。

### Q: 识别准确率不高？

A: 尝试以下方法：
- 提高图片分辨率
- 调整 `det_limit_side_len` 参数
- 预处理图片（去噪、二值化）

### Q: 如何识别英文？

A: `lang='ch'` 默认支持中英文混合。纯英文可用 `lang='en'`。

📖 完整 FAQ：[常见问题解决](docs/zh/troubleshooting.md)

---

## 项目结构

```
paddleocr-guide/
├── paddleocr_guide/         # CLI 命令行工具
│   ├── __init__.py
│   └── cli.py               # 命令行入口
├── examples/                # 示例代码 (16个)
│   ├── _common/             # 公共模块 (异常、日志、工具)
│   ├── basic/               # 基础示例 (3个)
│   ├── document/            # 文档处理 (3个)
│   └── advanced/            # 高级用法 (10个)
├── tests/                   # 测试代码
│   ├── conftest.py          # pytest fixtures
│   ├── test_common.py       # 公共模块测试
│   └── test_basic_ocr.py    # OCR 测试
├── docs/                    # 文档
│   ├── zh/                  # 中文文档
│   ├── en/                  # 英文文档
│   ├── ai-context/          # AI 协作上下文
│   └── development/         # 开发文档
├── .github/workflows/       # CI/CD 配置
├── assets/                  # 资源文件
├── pyproject.toml           # 项目配置
├── CHANGELOG.md             # 变更日志
└── CONTRIBUTING.md          # 贡献指南
```

---

## 贡献指南

欢迎贡献代码和文档！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

---

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 致谢

- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - 飞桨深度学习框架
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 百度 OCR 工具包

---

## 相关链接

- [PaddleOCR 官方文档](https://paddleocr.ai/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR-VL (HuggingFace)](https://huggingface.co/PaddlePaddle/PaddleOCR-VL)
