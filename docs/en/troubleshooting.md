# Troubleshooting Guide

This document covers common issues and solutions when using PaddleOCR.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [macOS Specific Issues](#macos-specific-issues)
- [Recognition Quality Issues](#recognition-quality-issues)
- [Performance Optimization](#performance-optimization)
- [Model Related Issues](#model-related-issues)

---

## Installation Issues

### Q1: pip install error "Could not find a version"

**Symptoms**:

```
ERROR: Could not find a version that satisfies the requirement paddleocr
```

**Cause**: Incompatible Python version or outdated pip

**Solution**:

```bash
# Upgrade pip
pip install --upgrade pip

# Check Python version (requires 3.8-3.11)
python --version

# Install specific version
pip install paddleocr==3.0.0
```

### Q2: Dependency Conflicts

**Symptoms**:

```
ERROR: Cannot install paddleocr because these package versions have conflicting dependencies
```

**Solution**:

```bash
# Use isolated virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # macOS/Linux
pip install paddleocr
```

### Q3: numpy Version Conflict

**Symptoms**:

```
numpy 2.x is incompatible with paddlepaddle
```

**Solution**:

```bash
pip install "numpy<2"
```

---

## Runtime Errors

### Q4: First Run Stuck at "Downloading model"

**Cause**: Model downloading, first run takes time (~10-50MB)

**Solution**:

1. Wait patiently (usually 1-5 minutes)
2. Or download models manually:

```python
ocr = PaddleOCR(
    det_model_dir='./models/det/',
    rec_model_dir='./models/rec/',
    cls_model_dir='./models/cls/'
)
```

### Q5: Out of Memory (OOM) / System Freeze

**Symptoms**:

```
MemoryError
```

Or process killed by system, or complete system freeze

**⚠️ Known Serious Issue (Under Investigation)**:

PaddleOCR 3.x may consume **40GB+ memory** on macOS ARM, even with small images.

**Possible Causes**:
1. PaddleOCR 3.x loads multiple preprocessing models simultaneously
2. PaddlePaddle framework memory management issues
3. macOS ARM platform compatibility issues

**Temporary Solutions**:

```python
# Method 1: Disable preprocessing models
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,  # Disable document orientation
    use_doc_unwarping=False,             # Disable document unwarping
    use_textline_orientation=False,      # Disable textline orientation
)

# Method 2: Reduce input size
ocr = PaddleOCR(
    lang='ch',
    det_limit_side_len=640,  # Reduce max side length (default 960)
    rec_batch_num=1          # Reduce batch size
)

# Method 3: Use lightweight model (to be verified)
# Try PP-OCRv5_mobile instead of PP-OCRv5_server
```

**Using CLI Tool Protection**:

```bash
# CLI automatically checks image size to prevent system freeze
paddleocr-guide scan large_image.png
# Error: File too large: 19.4MB (limit: 10MB)

# Force processing (at your own risk)
paddleocr-guide scan large_image.png --force
```

### Q6: Empty Recognition Results

**Possible Causes**:

1. Wrong image path
2. Unsupported image format
3. Poor image quality
4. Detection threshold too high

**Solution**:

```python
import os
from PIL import Image

# 1. Check image path
print(os.path.exists('your_image.png'))

# 2. Check image info
img = Image.open('your_image.png')
print(f"Size: {img.size}, Mode: {img.mode}")

# 3. Lower detection thresholds
ocr = PaddleOCR(
    det_db_thresh=0.1,      # Lower detection threshold
    det_db_box_thresh=0.3   # Lower text box threshold
)
```

### Q7: Encoding Errors

**Symptoms**:

```
UnicodeDecodeError: 'gbk' codec can't decode byte
```

**Solution**:

```python
# Ensure UTF-8 encoding when saving results
with open('result.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
```

---

## macOS Specific Issues

### Q8: PaddleOCR-VL Errors on Apple Silicon

**Symptoms**:

```
RuntimeError: Unsupported platform
ValueError: Image features and image tokens do not match
```

**Cause**: PaddleOCR-VL **does NOT support** ARM architecture

**Solution**:

Use PP-OCRv5 instead:

```python
from paddleocr import PaddleOCR

# This works on M1/M2/M3/M4
ocr = PaddleOCR(lang='ch')
result = ocr.predict('image.png')
```

### Q9: "illegal instruction" Error

**Cause**: Installed x86 version of packages

**Solution**:

```bash
# Complete uninstall
pip uninstall paddlepaddle paddleocr numpy opencv-python

# Reinstall (ensure ARM version)
pip install paddlepaddle paddleocr
```

### Q10: libiomp5.dylib Conflict

**Symptoms**:

```
OMP: Error #15: Initializing libiomp5.dylib, but found libiomp5.dylib already initialized.
```

**Solution**:

```python
# Add at the beginning of code
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Then import paddleocr
from paddleocr import PaddleOCR
```

### Q11: No GPU Acceleration

**Status**: macOS doesn't support CUDA, PaddlePaddle doesn't support Apple MPS yet

**Solution**:

```python
# Ensure CPU mode
ocr = PaddleOCR(use_gpu=False)

# Enable MKLDNN acceleration (CPU optimization)
ocr = PaddleOCR(enable_mkldnn=True)
```

---

## Recognition Quality Issues

### Q12: Low Recognition Accuracy

**Optimization Methods**:

```python
# 1. Increase input image size
ocr = PaddleOCR(det_limit_side_len=1280)  # default 960

# 2. Enable angle classification
ocr = PaddleOCR(use_angle_cls=True)

# 3. Image preprocessing
import cv2

def preprocess_image(img_path):
    img = cv2.imread(img_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Binarization
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

    return denoised

img = preprocess_image('noisy_image.png')
result = ocr.predict(img)
```

### Q13: Poor Tilted Text Recognition

**Solution**:

```python
# Enable angle classifier
ocr = PaddleOCR(use_angle_cls=True)
result = ocr.predict('tilted_image.png')
```

### Q14: Small Text Not Clear

**Solution**:

```python
# Increase detection input size
ocr = PaddleOCR(det_limit_side_len=1920)

# Or enlarge image first
from PIL import Image

img = Image.open('small_text.png')
img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
img.save('enlarged.png')

result = ocr.predict('enlarged.png')
```

### Q15: Vertical Text Recognition

**Solution**:

```python
# Enable angle classification
ocr = PaddleOCR(use_angle_cls=True)

# Or manually rotate image
from PIL import Image

img = Image.open('vertical_text.png')
img = img.rotate(90, expand=True)
result = ocr.predict(img)
```

---

## Performance Optimization

### Q16: CPU Inference Too Slow

**Optimization Methods**:

```python
# 1. Enable MKLDNN acceleration
ocr = PaddleOCR(enable_mkldnn=True, cpu_threads=4)

# 2. Reduce input size
ocr = PaddleOCR(det_limit_side_len=640)

# 3. Disable unnecessary features
ocr = PaddleOCR(use_angle_cls=False)  # If text is always upright

# 4. Reuse model instance
ocr = PaddleOCR()  # Initialize once
for img in images:
    result = ocr.predict(img)  # Call multiple times
```

### Q17: GPU Not Being Used

**Check Method**:

```python
import paddle
print(f"CUDA available: {paddle.device.is_compiled_with_cuda()}")
print(f"Current device: {paddle.device.get_device()}")
```

**Solution**:

```python
# Force GPU usage
ocr = PaddleOCR(use_gpu=True, gpu_mem=500)
```

### Q18: Batch Processing Optimization

```python
from paddleocr import PaddleOCR
from pathlib import Path

ocr = PaddleOCR(lang='ch')

def process_image(img_path):
    result = ocr.predict(str(img_path))
    return img_path.name, result

# Single-threaded sequential processing (recommended, avoids memory issues)
images = list(Path('images/').glob('*.png'))
for img_path in images:
    name, result = process_image(img_path)
    print(f"Done: {name}")
```

---

## Model Related Issues

### Q19: How to Use Custom Models?

```python
ocr = PaddleOCR(
    det_model_dir='./custom_models/det/',
    rec_model_dir='./custom_models/rec/',
    cls_model_dir='./custom_models/cls/',
    rec_char_dict_path='./custom_dict.txt'
)
```

### Q20: How to Change Model Download Source?

```bash
# Method 1: Environment variable
export PADDLE_PDX_MODEL_SOURCE=BOS

# Method 2: In code
import os
os.environ['PADDLE_PDX_MODEL_SOURCE'] = 'HuggingFace'
```

### Q21: Where Are Model Files Located?

Default download location: `~/.paddleocr/`

```bash
# View downloaded models
ls -la ~/.paddleocr/
```

---

## Getting More Help

If the above solutions don't solve your problem:

1. Check [PaddleOCR GitHub Issues](https://github.com/PaddlePaddle/PaddleOCR/issues)

2. When submitting a new Issue, include:
   - Operating system and version
   - Python version
   - PaddleOCR version
   - Complete error message
   - Minimal reproduction code

3. Community resources:
   - [PaddleOCR Official Documentation](https://paddleocr.ai/)
   - [PaddlePaddle Community](https://www.paddlepaddle.org.cn/)

---

## Next Steps

- [Installation Guide](installation.md)
- [Model Selection Guide](model_comparison.md)
- [Example Code](../../examples/)
