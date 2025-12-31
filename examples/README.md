# 示例代码索引

本目录包含 PaddleOCR 的各种使用示例。

---

## 目录结构

```
examples/
├── basic/                         # 基础示例 (PP-OCRv5)
│   ├── 01_simple_ocr.py           # 单图片 OCR
│   ├── 02_batch_ocr.py            # 批量处理
│   └── 03_multilingual.py         # 多语言识别
├── document/                      # 文档处理 (PP-StructureV3)
│   ├── 01_pdf_to_markdown.py      # PDF 转 Markdown
│   ├── 02_table_recognition.py    # 表格识别
│   └── 03_layout_analysis.py      # 版面分析
└── advanced/                      # 高级示例
    ├── 01_seal_recognition.py     # 印章识别 (PP-StructureV3)
    ├── 02_formula_recognition.py  # 公式识别 (PP-StructureV3)
    ├── 03_chart_recognition.py    # 图表识别 (PP-StructureV3)
    ├── 04_chatocr_extraction.py   # 智能抽取 (PP-ChatOCRv4Doc)
    ├── 05_handwriting_ocr.py      # 手写识别 (PP-OCRv5)
    ├── 06_vertical_text.py        # 竖排文字 (PP-OCRv5)
    ├── 07_doc_preprocessing.py    # 文档预处理 (PP-StructureV3)
    ├── 08_paddleocr_vl.py         # 视觉语言 (PaddleOCR-VL)
    ├── 09_doc_translation.py      # 文档翻译 (PP-DocTranslation)
    └── 10_doc_understanding.py    # 文档理解 (DocUnderstanding)
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

## 高级示例 (advanced/)

### 01_seal_recognition.py - 印章识别

**用途**: 识别文档中的公章、印章

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/advanced/01_seal_recognition.py
```

**主要功能**:
- 检测文档中的印章区域
- 提取印章中的文字
- 支持圆形、椭圆形印章

---

### 02_formula_recognition.py - 公式识别

**用途**: 识别数学公式并转换为 LaTeX

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/advanced/02_formula_recognition.py
```

**主要功能**:
- 检测公式区域
- 转换为 LaTeX 格式
- 支持行内和行间公式

---

### 03_chart_recognition.py - 图表识别

**用途**: 理解图表内容

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/advanced/03_chart_recognition.py
```

**主要功能**:
- 检测柱状图、折线图、饼图等
- 提取图表数据
- 理解图表含义

---

### 04_chatocr_extraction.py - 智能信息抽取

**用途**: 从票据、证件中提取结构化信息

**适用模型**: PP-ChatOCRv4Doc (离线模式)

**运行**:

```bash
python examples/advanced/04_chatocr_extraction.py
```

**主要功能**:
- 发票信息提取
- 身份证信息提取
- 合同信息提取
- 自定义 prompt 抽取

---

### 05_handwriting_ocr.py - 手写识别

**用途**: 识别手写文字

**适用模型**: PP-OCRv5

**运行**:

```bash
python examples/advanced/05_handwriting_ocr.py
```

**主要功能**:
- 识别潦草手写
- 处理倾斜文字
- 置信度过滤

---

### 06_vertical_text.py - 竖排文字

**用途**: 识别竖排/纵向排列的文字

**适用模型**: PP-OCRv5

**运行**:

```bash
python examples/advanced/06_vertical_text.py
```

**主要功能**:
- 中文竖排书籍识别
- 日文竖排文档
- 繁体中文支持

---

### 07_doc_preprocessing.py - 文档预处理

**用途**: 文档方向矫正、弯曲矫正

**适用模型**: PP-StructureV3

**运行**:

```bash
python examples/advanced/07_doc_preprocessing.py
```

**主要功能**:
- 文档方向检测与矫正 (0°/90°/180°/270°)
- 弯曲文档矫正
- 透视变形修复

---

### 08_paddleocr_vl.py - 视觉语言模型

**用途**: 使用 VL 模型进行复杂文档理解

**适用模型**: PaddleOCR-VL

> ⚠️ **注意**: 不支持 macOS ARM (M1/M2/M3/M4)

**运行**:

```bash
python examples/advanced/08_paddleocr_vl.py
```

**主要功能**:
- 109 种语言支持
- 复杂文档理解
- 图表、公式、表格综合识别

---

### 09_doc_translation.py - 文档翻译

**用途**: 保持版面结构的多语言翻译

**适用模型**: PP-DocTranslation

> ⚠️ **注意**: 需要配置 LLM API (如 ERNIE API)

**运行**:

```bash
python examples/advanced/09_doc_translation.py
```

**主要功能**:
- 识别文档版面结构
- 保持格式进行翻译
- 支持中英日韩等语言

---

### 10_doc_understanding.py - 文档理解

**用途**: 深度理解文档内容，回答问题

**适用模型**: DocUnderstanding (基于 VLM)

> ⚠️ **注意**: 需要 VLM 模型支持，不支持 macOS ARM

**运行**:

```bash
python examples/advanced/10_doc_understanding.py
```

**主要功能**:
- 文档内容问答
- 关键信息提取
- 上下文理解

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
