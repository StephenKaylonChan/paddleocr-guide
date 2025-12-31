# 示例代码索引

本目录包含 PaddleOCR 的各种使用示例。

---

## 目录结构

```
examples/
├── basic/                    # 基础示例
│   ├── 01_simple_ocr.py      # 单图片 OCR
│   ├── 02_batch_ocr.py       # 批量处理
│   └── 03_multilingual.py    # 多语言识别
├── document/                 # 文档处理
│   ├── 01_pdf_to_markdown.py # PDF 转 Markdown
│   ├── 02_table_recognition.py # 表格识别
│   └── 03_layout_analysis.py # 版面分析
└── advanced/                 # 高级示例
    └── (待添加)
```

---

## 基础示例 (basic/)

### 01_simple_ocr.py - 基础 OCR

**用途**: 单张图片的文字识别

**适用模型**: PP-OCRv5

**运行**:

```bash
python examples/basic/01_simple_ocr.py
```

**主要功能**:
- 初始化 OCR 引擎
- 识别图片中的文字
- 格式化输出结果

---

### 02_batch_ocr.py - 批量处理

**用途**: 批量处理目录中的所有图片

**适用模型**: PP-OCRv5

**运行**:

```bash
python examples/basic/02_batch_ocr.py
```

**主要功能**:
- 遍历目录中的所有图片
- 批量识别并保存结果
- 生成汇总报告 (JSON)

---

### 03_multilingual.py - 多语言识别

**用途**: 识别不同语言的文字

**适用模型**: PP-OCRv5

**运行**:

```bash
python examples/basic/03_multilingual.py
```

**主要功能**:
- 支持 80+ 种语言
- 自动检测最佳语言
- 中英混合识别

---

## 文档处理示例 (document/)

### 01_pdf_to_markdown.py - PDF 转换

**用途**: 将 PDF 或图片文档转换为 Markdown

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/document/01_pdf_to_markdown.py
```

**主要功能**:
- PDF/图片文档解析
- 输出 Markdown 格式
- 保留文档结构

---

### 02_table_recognition.py - 表格识别

**用途**: 识别并导出表格

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/document/02_table_recognition.py
```

**主要功能**:
- 检测图片中的表格
- 导出为 HTML/CSV 格式
- 支持复杂表格结构

**依赖**:

```bash
pip install pandas openpyxl  # 可选，用于导出 CSV/Excel
```

---

### 03_layout_analysis.py - 版面分析

**用途**: 分析文档版面结构

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/document/03_layout_analysis.py
```

**主要功能**:
- 识别标题、正文、表格、图片等
- 分析文档层次结构
- 输出版面分析报告

---

## 运行说明

### 前置条件

1. 安装依赖:

```bash
pip install paddleocr
```

2. 准备测试图片:

将测试图片放入 `assets/test_images/` 目录。

### 输出位置

所有示例的输出结果保存在 `assets/outputs/` 目录。

---

## 快速测试

```bash
# 运行基础 OCR 示例
cd /path/to/paddleocr-guide
python examples/basic/01_simple_ocr.py

# 查看输出
ls assets/outputs/
```

---

## 自定义使用

每个示例文件都可以作为独立模块导入:

```python
from examples.basic.simple_ocr import simple_ocr, format_result

# 使用函数
result = simple_ocr('your_image.png')
format_result(result)
```

---

## 下一步

- [安装指南](../docs/zh/installation.md)
- [模型选择指南](../docs/zh/model_comparison.md)
- [常见问题](../docs/zh/troubleshooting.md)
