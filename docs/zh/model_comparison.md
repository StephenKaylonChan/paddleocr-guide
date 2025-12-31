# 模型选择指南

本文档帮助你选择最适合场景的 PaddleOCR 模型。

---

## 目录

- [四大核心模型概览](#四大核心模型概览)
- [详细对比](#详细对比)
- [选择决策树](#选择决策树)
- [各模型使用示例](#各模型使用示例)
- [性能基准测试](#性能基准测试)

---

## 四大核心模型概览

PaddleOCR 3.0 提供四个核心模型，解决不同层次的问题：

| 模型 | 定位 | 一句话描述 |
|------|------|-----------|
| **PP-OCRv5** | 基础层 | 识别文字 |
| **PP-StructureV3** | 结构层 | 理解版面 |
| **PP-ChatOCRv4** | 应用层 | 问答交互 |
| **PaddleOCR-VL** | 智能层 | 端到端多模态理解 |

### 层次关系

```
PP-OCRv5          ← 基础层：识别文字
    ↓
PP-StructureV3    ← 结构层：理解版面
    ↓
PP-ChatOCRv4      ← 应用层：问答交互
    ↓
PaddleOCR-VL      ← 智能层：跳过前面所有步骤，直接理解
```

---

## 详细对比

### 功能对比

| 特性 | PP-OCRv5 | PP-StructureV3 | PP-ChatOCRv4 | PaddleOCR-VL |
|------|----------|----------------|--------------|--------------|
| 文字识别 | ✅ | ✅ | ✅ | ✅ |
| 表格识别 | ❌ | ✅ | ✅ | ✅ |
| 版面分析 | ❌ | ✅ | ✅ | ✅ |
| 公式识别 | ❌ | ✅ | ✅ | ✅ |
| 信息抽取 | ❌ | ❌ | ✅ | ✅ |
| 文档问答 | ❌ | ❌ | ✅ | ✅ |

### 技术规格

| 规格 | PP-OCRv5 | PP-StructureV3 | PP-ChatOCRv4 | PaddleOCR-VL |
|------|----------|----------------|--------------|--------------|
| 模型大小 | ~10MB | ~50MB | 需 LLM | ~900MB |
| 支持语言 | 80+ | 80+ | 80+ | 109 |
| macOS ARM | ✅ 支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| 离线运行 | ✅ | ✅ | ❌ 需 API | ✅ |
| 推理速度 | 快 | 中等 | 取决于 LLM | 较慢 |

### 技术路线

| 模型 | 技术路线 | 优势 | 劣势 |
|------|---------|------|------|
| PP-OCRv5 | 传统 CV (检测+识别) | 轻量、快速、可控 | 只认字，不理解语义 |
| PP-StructureV3 | CV + 规则 + 浅层理解 | 结构化输出 | 复杂逻辑理解有限 |
| PP-ChatOCRv4 | OCR + RAG + LLM | 智能理解 | 依赖大模型，成本高 |
| PaddleOCR-VL | 端到端 VLM | 直接理解，精度高 | 0.9B 参数，推理开销大 |

---

## 选择决策树

```
你的使用场景是？
│
├─ 【简单文字识别】
│   需求：只需要识别图片中的文字
│   └─ 推荐：PP-OCRv5 ⭐
│      - 最轻量（4.1MB）
│      - 支持中英日韩等语言
│      - macOS 完全兼容
│
├─ 【复杂文档处理】
│   需求：表格、PDF、版面分析
│   └─ 推荐：PP-StructureV3 ⭐
│      - 输出 Markdown/JSON
│      - 支持表格、公式、图表
│      - macOS 完全兼容
│
├─ 【票据/证件信息抽取】
│   需求：发票、身份证、合同关键信息
│   └─ 推荐：PP-ChatOCRv4 ⭐
│      - 智能抽取指定字段
│      - 需要配置 ERNIE API
│      - macOS 完全兼容
│
└─ 【多语言 / 视觉理解】
    需求：109种语言、复杂科研文档
    ├─ 有 x86/GPU
    │   └─ 推荐：PaddleOCR-VL ⭐
    │      - 端到端理解
    │      - 精度最高
    │
    └─ macOS ARM
        └─ 推荐：PP-OCRv5
           - VL 模型不支持
           - 功能受限
```

---

## 各模型使用示例

### PP-OCRv5 - 基础文字识别

```python
from paddleocr import PaddleOCR

# 初始化
ocr = PaddleOCR(
    use_angle_cls=True,  # 方向分类
    lang='ch',           # 中文（同时支持英文）
    show_log=False
)

# 识别
result = ocr.ocr('image.png', cls=True)

# 输出
for line in result[0]:
    box, (text, confidence) = line[0], line[1]
    print(f"{text} ({confidence:.2%})")
```

### PP-StructureV3 - 文档结构解析

```python
from paddleocr import PPStructure

# 初始化
structure = PPStructure(
    recovery=True,                    # 版面恢复
    return_ocr_result_in_table=True,  # 返回表格内 OCR 结果
    show_log=False
)

# 解析文档
result = structure('document.pdf')

# 处理结果
for item in result:
    print(f"类型: {item['type']}")
    if item['type'] == 'table':
        print(f"表格 HTML: {item['res']['html']}")
    elif item['type'] == 'text':
        print(f"文本: {item['res']['text']}")
```

### PP-ChatOCRv4 - 智能信息抽取

```python
from paddleocr import PPChatOCR
import os

# 配置 ERNIE API
os.environ['ERNIE_API_KEY'] = 'your-api-key'

# 初始化
chat_ocr = PPChatOCR()

# 定义要抽取的字段
keys = ["发票号码", "开票日期", "金额", "税额"]

# 抽取信息
result = chat_ocr('invoice.png', keys=keys)

print(result)
```

### PaddleOCR-VL - 视觉语言模型

```python
# 注意：不支持 macOS ARM！
from transformers import AutoModel, AutoProcessor
from PIL import Image

# 加载模型
model_path = "PaddlePaddle/PaddleOCR-VL"
model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

# 识别
image = Image.open('document.png')
inputs = processor(
    text="识别图片中的所有文字和表格",
    images=image,
    return_tensors="pt"
)
outputs = model.generate(**inputs)
result = processor.batch_decode(outputs, skip_special_tokens=True)

print(result)
```

---

## 性能基准测试

### 中文场景准确率

数据集：ICDAR 2017 中文场景文字

| 模型 | 检测 | 识别 | 端到端 |
|------|------|------|--------|
| PP-OCRv5 | 95.2% | 93.8% | 89.7% |
| PP-StructureV3 | 94.1% | 92.5% | 87.3% |
| PaddleOCR-VL | 96.8% | 95.2% | 92.1% |

### 推理速度

测试环境：单张 1920x1080 图片

| 模型 | CPU (M1 Mac) | CPU (Intel) | GPU (RTX 3090) |
|------|-------------|-------------|----------------|
| PP-OCRv5 | ~300ms | ~200ms | ~50ms |
| PP-StructureV3 | ~800ms | ~500ms | ~150ms |
| PaddleOCR-VL | ❌ 不支持 | ~3000ms | ~300ms |

### 内存占用

| 模型 | 加载后内存 | 推理峰值内存 |
|------|-----------|-------------|
| PP-OCRv5 | ~500MB | ~1GB |
| PP-StructureV3 | ~800MB | ~2GB |
| PaddleOCR-VL | ~4GB | ~6GB |

---

## 推荐选择

### 按场景推荐

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 个人学习/小项目 | PP-OCRv5 | 简单、快速、免费 |
| 企业文档处理 | PP-StructureV3 | 结构化输出、生产级 |
| 票据/合同处理 | PP-ChatOCRv4 | 智能抽取、准确率高 |
| 科研/多语言 | PaddleOCR-VL | 功能最强（需 x86/GPU）|

### 按硬件推荐

| 硬件 | 推荐模型 |
|------|---------|
| macOS M1/M2/M3 | PP-OCRv5, PP-StructureV3 |
| macOS Intel | 全部支持 |
| Linux + GPU | 全部支持（推荐 VL）|
| Windows | 全部支持 |

---

## 下一步

- [安装指南](installation.md)
- [常见问题](troubleshooting.md)
- [示例代码](../../examples/)
