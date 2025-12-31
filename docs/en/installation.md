# Installation Guide

This document provides detailed instructions for installing PaddleOCR and configuring the environment.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [macOS Notes](#macos-notes)
- [GPU Acceleration](#gpu-acceleration)
- [Verify Installation](#verify-installation)
- [Common Issues](#common-issues)

---

## System Requirements

### Operating Systems

| System | Support Status | Notes |
|--------|----------------|-------|
| macOS (Intel) | ✅ Fully supported | |
| macOS (M1/M2/M3/M4) | ⚠️ Partial support | VL models not available |
| Ubuntu 18.04+ | ✅ Fully supported | Recommended |
| Windows 10+ | ✅ Fully supported | |

### Python Version

- **Minimum**: Python 3.8
- **Recommended**: Python 3.9 - 3.11
- **Note**: Python 3.12+ may have compatibility issues

### Hardware Requirements

| Configuration | Minimum | Recommended |
|---------------|---------|-------------|
| Memory | 4GB | 8GB+ |
| Storage | 2GB | 5GB+ |
| GPU | None | NVIDIA CUDA 11.x |

---

## Installation Methods

### Method 1: pip (Recommended)

```bash
# Basic installation
pip install paddleocr

# Full installation (with all optional dependencies)
pip install "paddleocr[all]"
```

### Method 2: Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install
pip install paddleocr
```

### Method 3: Using conda

```bash
conda create -n paddleocr python=3.10
conda activate paddleocr
pip install paddleocr
```

### Method 4: From Source

```bash
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR
pip install -r requirements.txt
pip install -e .
```

---

## macOS Notes

### Apple Silicon (M1/M2/M3/M4) Users

#### Important Limitation

> ⚠️ **PaddleOCR-VL models are NOT supported on Apple Silicon chips**

#### Solutions

1. **Use PP-OCRv5** (Recommended)
   - Full functionality
   - Excellent performance
   - Fully compatible with ARM architecture

2. **Use Docker** (if VL models needed)
   - Runs via x86 emulation
   - Significant performance penalty

#### Correct Installation

```bash
# Ensure using native ARM Python
which python  # Should show ARM version path

# Install
pip install paddleocr paddlepaddle
```

### Intel Mac Users

All features fully supported. Follow standard installation process.

---

## GPU Acceleration

### NVIDIA GPU (CUDA)

```bash
# Check CUDA version
nvcc --version

# Install corresponding PaddlePaddle GPU version
pip install paddlepaddle-gpu==3.0.0 -i https://mirror.baidu.com/pypi/simple
```

### Apple GPU (MPS)

PaddlePaddle **does not support** Apple MPS acceleration. Falls back to CPU automatically.

### No GPU

```python
# Ensure CPU mode
ocr = PaddleOCR(use_gpu=False)
```

---

## Verify Installation

### Basic Verification

```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR installed successfully')"
```

### Functionality Verification

```python
from paddleocr import PaddleOCR

# Initialize (first run downloads models)
ocr = PaddleOCR(lang='ch')

print('OCR engine initialized successfully')
```

### Complete Test

```python
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

# Create test image
img = Image.new('RGB', (200, 50), color='white')
img_array = np.array(img)

# Test recognition
ocr = PaddleOCR(lang='ch')
result = ocr.predict(img_array)

print('Complete test passed')
```

---

## Common Issues

### Issue 1: ModuleNotFoundError: No module named 'paddle'

**Cause**: PaddlePaddle not properly installed

**Solution**:

```bash
pip uninstall paddlepaddle
pip install paddlepaddle
```

### Issue 2: Model Download Fails

**Cause**: Network issues or unavailable mirror

**Solution**:

```bash
# Method 1: Set mirror source
export PADDLE_PDX_MODEL_SOURCE=BOS

# Method 2: Use proxy
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### Issue 3: "illegal instruction" on macOS

**Cause**: Installed incompatible ARM package

**Solution**:

```bash
pip uninstall paddlepaddle paddleocr numpy opencv-python
pip install paddlepaddle paddleocr
```

### Issue 4: numpy Version Conflict

**Cause**: numpy 2.x incompatible with some dependencies

**Solution**:

```bash
pip install "numpy<2"
```

### Issue 5: Slow Installation

**Solution**: Use mirrors

```bash
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Next Steps

- [Quick Start](quickstart.md)
- [Model Selection Guide](model_comparison.md)
- [Troubleshooting](troubleshooting.md)
