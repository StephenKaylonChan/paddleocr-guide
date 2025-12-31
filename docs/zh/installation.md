# 安装指南

本文档详细介绍 PaddleOCR 的安装步骤和环境配置。

---

## 目录

- [系统要求](#系统要求)
- [安装方式](#安装方式)
- [macOS 特别说明](#macos-特别说明)
- [GPU 加速配置](#gpu-加速配置)
- [验证安装](#验证安装)
- [常见安装问题](#常见安装问题)

---

## 系统要求

### 操作系统

| 系统 | 支持状态 | 备注 |
|------|---------|------|
| macOS (Intel) | ✅ 完全支持 | |
| macOS (M1/M2/M3/M4) | ⚠️ 部分支持 | VL 模型不可用 |
| Ubuntu 18.04+ | ✅ 完全支持 | 推荐 |
| Windows 10+ | ✅ 完全支持 | |

### Python 版本

- **最低要求**: Python 3.8
- **推荐版本**: Python 3.9 - 3.11
- **注意**: Python 3.12+ 可能存在兼容性问题

### 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 内存 | 4GB | 8GB+ |
| 存储 | 2GB | 5GB+ |
| GPU | 无 | NVIDIA CUDA 11.x |

---

## 安装方式

### 方式一：pip 安装（推荐）

```bash
# 基础安装
pip install paddleocr

# 完整安装（包含所有可选依赖）
pip install "paddleocr[all]"
```

### 方式二：使用虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装
pip install paddleocr
```

### 方式三：使用 conda

```bash
conda create -n paddleocr python=3.10
conda activate paddleocr
pip install paddleocr
```

### 方式四：从源码安装

```bash
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR
pip install -r requirements.txt
pip install -e .
```

---

## macOS 特别说明

### Apple Silicon (M1/M2/M3/M4) 用户

#### 重要限制

> ⚠️ **PaddleOCR-VL 模型不支持 Apple Silicon 芯片**

#### 解决方案

1. **使用 PP-OCRv5**（推荐）
   - 功能完整
   - 性能优秀
   - 完全兼容 ARM 架构

2. **使用 Docker**（如需 VL 模型）
   - 通过 x86 模拟运行
   - 性能损失较大

#### 正确的安装方式

```bash
# 确保使用原生 ARM Python
which python  # 应显示 ARM 版本路径

# 安装
pip install paddleocr paddlepaddle
```

### Intel Mac 用户

完全支持所有功能，按标准流程安装即可。

---

## GPU 加速配置

### NVIDIA GPU (CUDA)

```bash
# 检查 CUDA 版本
nvcc --version

# 安装对应版本的 PaddlePaddle GPU 版
pip install paddlepaddle-gpu==3.0.0 -i https://mirror.baidu.com/pypi/simple
```

### Apple GPU (MPS)

当前 PaddlePaddle **不支持** Apple MPS 加速，自动使用 CPU。

### 无 GPU 情况

```python
# 确保使用 CPU 模式
ocr = PaddleOCR(use_gpu=False)
```

---

## 验证安装

### 基础验证

```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功')"
```

### 功能验证

```python
from paddleocr import PaddleOCR

# 初始化（首次运行会下载模型）
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

print('OCR 引擎初始化成功')
```

### 完整测试

```python
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

# 创建测试图片
img = Image.new('RGB', (200, 50), color='white')
img_array = np.array(img)

# 测试识别
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
result = ocr.ocr(img_array, cls=True)

print('完整测试通过')
```

---

## 常见安装问题

### 问题 1: ModuleNotFoundError: No module named 'paddle'

**原因**: PaddlePaddle 未正确安装

**解决**:

```bash
pip uninstall paddlepaddle
pip install paddlepaddle
```

### 问题 2: 模型下载失败

**原因**: 网络问题或镜像源不可用

**解决**:

```bash
# 方法 1: 设置镜像源
export PADDLE_PDX_MODEL_SOURCE=BOS

# 方法 2: 使用代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### 问题 3: macOS 上出现 "illegal instruction"

**原因**: 使用了不兼容 ARM 的包

**解决**:

```bash
pip uninstall paddlepaddle paddleocr numpy opencv-python
pip install paddlepaddle paddleocr
```

### 问题 4: numpy 版本冲突

**原因**: numpy 2.x 与部分依赖不兼容

**解决**:

```bash
pip install "numpy<2"
```

### 问题 5: 安装速度慢

**解决**: 使用国内镜像

```bash
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 下一步

- [快速入门](quickstart.md)
- [模型选择指南](model_comparison.md)
- [常见问题解决](troubleshooting.md)
