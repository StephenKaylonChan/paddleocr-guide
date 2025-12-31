# PaddleOCR Practical Guide

> A Chinese OCR solution based on PaddleOCR 3.0, optimized for macOS users

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.x-green.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**English** | [中文](README.md)

**GitHub**: [stephenkaylonchan/paddleocr-guide](https://github.com/stephenkaylonchan/paddleocr-guide)

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Quick Start](#quick-start)
- [Model Selection Guide](#model-selection-guide)
- [Examples](#examples)
- [macOS Users Guide](#macos-users-guide)
- [FAQ](#faq)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## Introduction

This project provides practical examples and best practices for PaddleOCR 3.0, helping developers quickly get started with Chinese OCR (Optical Character Recognition).

**Why PaddleOCR?**

- Ultra-lightweight models (PP-OCRv5 is only 4.1MB)
- 80+ language support
- Ready to use, no training required
- Supports document parsing, table recognition, information extraction

---

## Features

| Feature | Description | Example |
|---------|-------------|---------|
| Basic OCR | Image text recognition | [01_simple_ocr.py](examples/basic/01_simple_ocr.py) |
| Batch Processing | Multi-image batch recognition | [02_batch_ocr.py](examples/basic/02_batch_ocr.py) |
| Multilingual | Chinese, English, Japanese, Korean, etc. | [03_multilingual.py](examples/basic/03_multilingual.py) |
| Table Recognition | Recognize and export tables | [02_table_recognition.py](examples/document/02_table_recognition.py) |
| PDF Conversion | PDF to Markdown | [01_pdf_to_markdown.py](examples/document/01_pdf_to_markdown.py) |

---

## Quick Start

### Requirements

- Python 3.8+
- macOS / Linux / Windows

### Installation

```bash
# Basic installation
pip install paddleocr

# Full installation (recommended)
pip install "paddleocr[all]"
```

### Verify Installation

```bash
python -c "from paddleocr import PaddleOCR; print('Installation successful')"
```

### First OCR Program

```python
from paddleocr import PaddleOCR

# Initialize (models will be downloaded automatically on first run)
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# Recognize image
result = ocr.ocr('your_image.png', cls=True)

# Output results
for line in result[0]:
    text, confidence = line[1]
    print(f"Text: {text}, Confidence: {confidence:.2%}")
```

---

## Model Selection Guide

PaddleOCR 3.0 provides four core models:

| Model | Purpose | macOS ARM | Model Size | Use Case |
|-------|---------|-----------|------------|----------|
| **PP-OCRv5** | Traditional OCR | ✅ Fully supported | ~10MB | General text recognition |
| **PP-StructureV3** | Document parsing | ✅ Fully supported | ~50MB | Tables/PDF/Layout analysis |
| **PP-ChatOCRv4** | Smart extraction | ✅ Fully supported | - | Invoice/ID card info extraction |
| **PaddleOCR-VL** | Vision-language | ❌ Not supported | ~900MB | 109 languages/Complex documents |

### How to Choose?

```
What's your use case?
│
├─ Simple text recognition → PP-OCRv5 ✅
│
├─ Complex documents/Tables/PDF → PP-StructureV3 ✅
│
├─ Invoice/ID card extraction → PP-ChatOCRv4 ✅
│
└─ 109 languages / Visual understanding
   ├─ Have x86/GPU → PaddleOCR-VL ✅
   └─ macOS ARM → PP-OCRv5 (limited features) ⚠️
```

---

## Examples

### Basic OCR

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('image.png', cls=True)

for line in result[0]:
    print(f"Text: {line[1][0]}")
```

### Table Recognition

```python
from paddleocr import PPStructure

structure = PPStructure(recovery=True, return_ocr_result_in_table=True)
result = structure('table.png')

for item in result:
    if item['type'] == 'table':
        print(item['res']['html'])  # HTML format table
```

More examples: [examples/](examples/)

---

## macOS Users Guide

### Important Limitation

> ⚠️ **PaddleOCR-VL does NOT support Apple Silicon (M1/M2/M3/M4)**

If you're using a Mac with M-series chip, please use **PP-OCRv5** instead.

### Recommended Solutions

| Scenario | Recommended Model | Notes |
|----------|-------------------|-------|
| General text recognition | PP-OCRv5 | Fully compatible |
| Document parsing | PP-StructureV3 | Fully compatible |
| Info extraction | PP-ChatOCRv4 | Requires ERNIE API |
| Multilingual | PP-OCRv5 | Supports Chinese, English, Japanese, Korean, etc. |

### Common Errors and Solutions

#### 1. `illegal instruction` error

```bash
# Cause: Installed x86 version packages
# Solution: Reinstall native ARM version
pip uninstall paddlepaddle paddleocr
pip install paddlepaddle paddleocr
```

#### 2. `libiomp5.dylib` conflict

```python
# Add at the beginning of your code
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

---

## FAQ

### Q: First run is very slow?

A: First run will automatically download models (~10MB), please be patient.

### Q: Recognition accuracy is not high?

A: Try the following methods:
- Increase image resolution
- Adjust `det_limit_side_len` parameter
- Preprocess image (denoise, binarize)

### Q: How to recognize English?

A: `lang='ch'` supports Chinese-English mixed recognition by default. Use `lang='en'` for pure English.

---

## Project Structure

```
paddleocr-guide/
├── docs/                    # Documentation
│   └── zh/                  # Chinese docs
├── examples/                # Example code
│   ├── basic/               # Basic examples
│   └── document/            # Document processing
├── assets/                  # Resources
│   ├── test_images/         # Test images
│   └── outputs/             # Output directory
├── README.md                # Chinese README (main)
├── README_en.md             # English README (this file)
├── requirements.txt         # Dependencies
└── LICENSE                  # License
```

---

## Contributing

Contributions are welcome!

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a Pull Request

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - Deep learning framework
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Baidu OCR toolkit

---

## Links

- [PaddleOCR Official Documentation](https://paddleocr.ai/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR-VL (HuggingFace)](https://huggingface.co/PaddlePaddle/PaddleOCR-VL)
