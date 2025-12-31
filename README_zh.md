# PaddleOCR 实战指南

> 基于 PaddleOCR 3.0 的中文 OCR 解决方案，专为 macOS 用户优化

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.x-green.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | 中文

**GitHub**: [stephenkaylonchan/paddleocr-guide](https://github.com/stephenkaylonchan/paddleocr-guide)

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
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
| 基础 OCR | 图片文字识别 | [01_simple_ocr.py](examples/basic/01_simple_ocr.py) |
| 批量处理 | 多图片批量识别 | [02_batch_ocr.py](examples/basic/02_batch_ocr.py) |
| 多语言 | 中英日韩等语言 | [03_multilingual.py](examples/basic/03_multilingual.py) |
| 表格识别 | 识别并导出表格 | [02_table_recognition.py](examples/document/02_table_recognition.py) |
| PDF 转换 | PDF 转 Markdown | [01_pdf_to_markdown.py](examples/document/01_pdf_to_markdown.py) |

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
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 识别图片
result = ocr.ocr('your_image.png', cls=True)

# 输出结果
for line in result[0]:
    text, confidence = line[1]
    print(f"文本: {text}, 置信度: {confidence:.2%}")
```

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

---

## 使用示例

### 基础 OCR

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('image.png', cls=True)

for line in result[0]:
    print(f"文本: {line[1][0]}")
```

### 表格识别

```python
from paddleocr import PPStructure

structure = PPStructure(recovery=True, return_ocr_result_in_table=True)
result = structure('table.png')

for item in result:
    if item['type'] == 'table':
        print(item['res']['html'])  # HTML 格式表格
```

### 批量处理

```python
from pathlib import Path
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

for img_path in Path('images/').glob('*.png'):
    result = ocr.ocr(str(img_path), cls=True)
    print(f"\n{img_path.name}:")
    for line in result[0]:
        print(f"  {line[1][0]}")
```

📖 更多示例：[examples/](examples/)

---

## macOS 用户须知

### 重要限制

> ⚠️ **PaddleOCR-VL 不支持 Apple Silicon (M1/M2/M3/M4)**

如果你使用的是 M 系列芯片的 Mac，请使用 **PP-OCRv5** 替代。

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
├── docs/                    # 文档
│   ├── zh/                  # 中文文档
│   │   ├── installation.md  # 安装指南
│   │   ├── model_comparison.md  # 模型对比
│   │   └── troubleshooting.md   # 常见问题
│   └── en/                  # 英文文档
├── examples/                # 示例代码
│   ├── basic/               # 基础示例
│   ├── document/            # 文档处理
│   └── advanced/            # 高级用法
├── assets/                  # 资源文件
│   ├── test_images/         # 测试图片
│   └── outputs/             # 输出目录
├── scripts/                 # 脚本工具
├── README.md                # 英文 README
├── README_zh.md             # 中文 README（本文件）
├── requirements.txt         # 依赖
└── LICENSE                  # 许可证
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
