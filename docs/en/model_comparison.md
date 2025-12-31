# Model Selection Guide

This document helps you choose the most suitable PaddleOCR model for your use case.

---

## Table of Contents

- [Core Models Overview](#core-models-overview)
- [Detailed Comparison](#detailed-comparison)
- [Selection Decision Tree](#selection-decision-tree)
- [Usage Examples](#usage-examples)
- [Performance Benchmarks](#performance-benchmarks)

---

## Core Models Overview

PaddleOCR 3.0 provides four core models for different levels of complexity:

| Model | Level | One-liner Description |
|-------|-------|----------------------|
| **PP-OCRv5** | Foundation | Recognize text |
| **PP-StructureV3** | Structure | Understand layout |
| **PP-ChatOCRv4** | Application | Q&A interaction |
| **PaddleOCR-VL** | Intelligence | End-to-end multimodal understanding |

### Layer Relationship

```
PP-OCRv5          ← Foundation: Recognize text
    ↓
PP-StructureV3    ← Structure: Understand layout
    ↓
PP-ChatOCRv4      ← Application: Q&A interaction
    ↓
PaddleOCR-VL      ← Intelligence: Skip all above, understand directly
```

---

## Detailed Comparison

### Feature Comparison

| Feature | PP-OCRv5 | PP-StructureV3 | PP-ChatOCRv4 | PaddleOCR-VL |
|---------|----------|----------------|--------------|--------------|
| Text recognition | ✅ | ✅ | ✅ | ✅ |
| Table recognition | ❌ | ✅ | ✅ | ✅ |
| Layout analysis | ❌ | ✅ | ✅ | ✅ |
| Formula recognition | ❌ | ✅ | ✅ | ✅ |
| Information extraction | ❌ | ❌ | ✅ | ✅ |
| Document Q&A | ❌ | ❌ | ✅ | ✅ |

### Technical Specifications

| Spec | PP-OCRv5 | PP-StructureV3 | PP-ChatOCRv4 | PaddleOCR-VL |
|------|----------|----------------|--------------|--------------|
| Model size | ~10MB | ~50MB | Requires LLM | ~900MB |
| Languages | 80+ | 80+ | 80+ | 109 |
| macOS ARM | ✅ Supported | ✅ Supported | ✅ Supported | ❌ Not supported |
| Offline | ✅ | ✅ | ❌ Needs API | ✅ |
| Speed | Fast | Medium | Depends on LLM | Slower |

### Technical Approach

| Model | Approach | Advantages | Disadvantages |
|-------|----------|------------|---------------|
| PP-OCRv5 | Traditional CV (detection + recognition) | Lightweight, fast, controllable | Only recognizes text, no semantic understanding |
| PP-StructureV3 | CV + rules + shallow understanding | Structured output | Limited complex logic understanding |
| PP-ChatOCRv4 | OCR + RAG + LLM | Intelligent understanding | Relies on LLM, high cost |
| PaddleOCR-VL | End-to-end VLM | Direct understanding, high accuracy | 0.9B parameters, high inference cost |

---

## Selection Decision Tree

```
What is your use case?
│
├─ 【Simple Text Recognition】
│   Need: Just recognize text in images
│   └─ Recommend: PP-OCRv5 ⭐
│      - Lightest (4.1MB)
│      - Supports Chinese, English, Japanese, Korean, etc.
│      - Fully compatible with macOS
│
├─ 【Complex Document Processing】
│   Need: Tables, PDFs, layout analysis
│   └─ Recommend: PP-StructureV3 ⭐
│      - Output Markdown/JSON
│      - Supports tables, formulas, charts
│      - Fully compatible with macOS
│
├─ 【Invoice/ID Card Information Extraction】
│   Need: Invoice, ID card, contract key information
│   └─ Recommend: PP-ChatOCRv4 ⭐
│      - Intelligent field extraction
│      - Requires ERNIE API configuration
│      - Fully compatible with macOS
│
└─ 【Multi-language / Visual Understanding】
    Need: 109 languages, complex research documents
    ├─ Have x86/GPU
    │   └─ Recommend: PaddleOCR-VL ⭐
    │      - End-to-end understanding
    │      - Highest accuracy
    │
    └─ macOS ARM
        └─ Recommend: PP-OCRv5
           - VL model not supported
           - Limited functionality
```

---

## Usage Examples

### PP-OCRv5 - Basic Text Recognition

```python
from paddleocr import PaddleOCR

# Initialize
ocr = PaddleOCR(lang='ch')

# Recognize
result = ocr.predict('image.png')

# Output
for res in result:
    res.print()
```

### PP-StructureV3 - Document Structure Parsing

```python
from paddleocr import PPStructureV3

# Initialize
structure = PPStructureV3(
    use_table_recognition=True,
    use_formula_recognition=True
)

# Parse document
result = structure.predict('document.pdf')

# Process results
for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')
```

### PP-ChatOCRv4 - Intelligent Information Extraction

```python
from paddleocr import PPChatOCRv4Doc

# Initialize (offline mode)
chat_ocr = PPChatOCRv4Doc(
    use_seal_recognition=True,
    use_table_recognition=True
)

# Visual analysis
visual_result = chat_ocr.visual_predict(input='invoice.png')

# Build vector
vector_info = chat_ocr.build_vector(visual_result)

# Extract information
result = chat_ocr.chat(
    key_list=['Invoice Number', 'Amount', 'Date'],
    visual_info=visual_result,
    vector_info=vector_info
)

print(result['chat_res'])
```

### PaddleOCR-VL - Vision Language Model

```python
# Note: NOT supported on macOS ARM!
from paddleocr import PaddleOCRVL

# Local inference
vl = PaddleOCRVL(
    use_doc_orientation_classify=True,
    use_layout_detection=True
)

result = vl.predict('complex_document.pdf')

for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')
```

---

## Performance Benchmarks

### Chinese Scene Accuracy

Dataset: ICDAR 2017 Chinese Scene Text

| Model | Detection | Recognition | End-to-end |
|-------|-----------|-------------|------------|
| PP-OCRv5 | 95.2% | 93.8% | 89.7% |
| PP-StructureV3 | 94.1% | 92.5% | 87.3% |
| PaddleOCR-VL | 96.8% | 95.2% | 92.1% |

### Inference Speed

Test environment: Single 1920x1080 image

| Model | CPU (M1 Mac) | CPU (Intel) | GPU (RTX 3090) |
|-------|--------------|-------------|----------------|
| PP-OCRv5 | ~300ms | ~200ms | ~50ms |
| PP-StructureV3 | ~800ms | ~500ms | ~150ms |
| PaddleOCR-VL | ❌ Not supported | ~3000ms | ~300ms |

### Memory Usage

| Model | After Loading | Peak During Inference |
|-------|---------------|----------------------|
| PP-OCRv5 | ~500MB | ~1GB |
| PP-StructureV3 | ~800MB | ~2GB |
| PaddleOCR-VL | ~4GB | ~6GB |

---

## Recommendations

### By Use Case

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| Personal learning/small projects | PP-OCRv5 | Simple, fast, free |
| Enterprise document processing | PP-StructureV3 | Structured output, production-grade |
| Invoice/contract processing | PP-ChatOCRv4 | Intelligent extraction, high accuracy |
| Research/multi-language | PaddleOCR-VL | Most powerful (requires x86/GPU) |

### By Hardware

| Hardware | Recommended Models |
|----------|-------------------|
| macOS M1/M2/M3/M4 | PP-OCRv5, PP-StructureV3 |
| macOS Intel | All supported |
| Linux + GPU | All supported (recommend VL) |
| Windows | All supported |

---

## Next Steps

- [Installation Guide](installation.md)
- [Troubleshooting](troubleshooting.md)
- [Example Code](../../examples/)
