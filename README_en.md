# PaddleOCR Practical Guide

> A Chinese OCR solution based on PaddleOCR 3.0, optimized for macOS users

[![CI](https://github.com/StephenKaylonChan/paddleocr-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/StephenKaylonChan/paddleocr-guide/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.x-green.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**English** | [中文](README.md)

**GitHub**: [stephenkaylonchan/paddleocr-guide](https://github.com/stephenkaylonchan/paddleocr-guide)

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Quick Start](#quick-start)
- [CLI Tool](#cli-tool)
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
ocr = PaddleOCR(lang='ch')

# Recognize image (PaddleOCR 3.x API)
result = ocr.predict('your_image.png')

# Output results
for res in result:
    res.print()  # Print results directly
    # Or get JSON format
    # print(res.json)
```

---

## CLI Tool

Use directly in terminal after installation, no coding required:

```bash
# Install
pip install -e .

# View help
paddleocr-guide --help
```

### Available Commands

| Command | Function | Example |
|---------|----------|---------|
| `scan` | Recognize single image | `paddleocr-guide scan photo.png` |
| `batch` | Batch process directory | `paddleocr-guide batch ./images/` |
| `pdf` | PDF to Markdown | `paddleocr-guide pdf doc.pdf -o out.md` |
| `langs` | List supported languages | `paddleocr-guide langs` |
| `info` | Show environment info | `paddleocr-guide info` |

> **Note**: CLI has built-in image size check. Images over 10MB or 16 million pixels will be rejected. Use `--force` to override.

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

### Basic OCR (PaddleOCR 3.x)

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch')
result = ocr.predict('image.png')

for res in result:
    res.print()
```

### Table Recognition (PPStructureV3)

```python
from paddleocr import PPStructureV3

pipeline = PPStructureV3(use_table_recognition=True)
result = pipeline.predict(input='table.png')

for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')
```

More examples: [examples/](examples/)

---

## macOS Users Guide

### Important Limitation

> ⚠️ **PaddleOCR-VL does NOT support Apple Silicon (M1/M2/M3/M4)**

If you're using a Mac with M-series chip, please use **PP-OCRv5** instead.

### Known Issue: High Memory Usage

> ⚠️ **PaddleOCR 3.x may consume excessive memory (40GB+) on macOS ARM, potentially causing system freeze**

**Temporary Solution**:
```python
# Disable preprocessing models to reduce memory usage
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
```

See [Troubleshooting](docs/en/troubleshooting.md) for details.

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
├── paddleocr_guide/         # CLI command line tool
│   ├── __init__.py
│   └── cli.py               # CLI entry point
├── examples/                # Example code (16 files)
│   ├── _common/             # Common modules (exceptions, logging, utils)
│   ├── basic/               # Basic examples (3)
│   ├── document/            # Document processing (3)
│   └── advanced/            # Advanced examples (10)
├── tests/                   # Test code
│   ├── conftest.py          # pytest fixtures
│   ├── test_common.py       # Common module tests
│   └── test_basic_ocr.py    # OCR tests
├── docs/                    # Documentation
│   ├── zh/                  # Chinese docs
│   ├── en/                  # English docs
│   ├── ai-context/          # AI collaboration context
│   └── development/         # Development docs
├── .github/workflows/       # CI/CD configuration
├── assets/                  # Resources
├── pyproject.toml           # Project configuration
├── CHANGELOG.md             # Changelog
└── CONTRIBUTING.md          # Contributing guide
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
