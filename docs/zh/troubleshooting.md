# 常见问题与解决方案

本文档汇总 PaddleOCR 使用过程中的常见问题及解决方案。

---

## 目录

- [安装问题](#安装问题)
- [运行时错误](#运行时错误)
- [macOS 特有问题](#macos-特有问题)
- [识别效果问题](#识别效果问题)
- [性能优化](#性能优化)
- [模型相关问题](#模型相关问题)

---

## 安装问题

### Q1: pip install 报错 "Could not find a version"

**症状**:

```
ERROR: Could not find a version that satisfies the requirement paddleocr
```

**原因**: Python 版本不兼容或 pip 版本过旧

**解决**:

```bash
# 升级 pip
pip install --upgrade pip

# 检查 Python 版本（需要 3.8-3.11）
python --version

# 指定版本安装
pip install paddleocr==3.0.0
```

### Q2: 依赖冲突

**症状**:

```
ERROR: Cannot install paddleocr because these package versions have conflicting dependencies
```

**解决**:

```bash
# 使用独立虚拟环境
python -m venv fresh_env
source fresh_env/bin/activate  # macOS/Linux
pip install paddleocr
```

### Q3: numpy 版本冲突

**症状**:

```
numpy 2.x is incompatible with paddlepaddle
```

**解决**:

```bash
pip install "numpy<2"
```

---

## 运行时错误

### Q4: 首次运行卡在 "Downloading model"

**原因**: 模型下载中，首次需要时间（约 10-50MB）

**解决**:

1. 耐心等待（通常 1-5 分钟）
2. 或手动下载模型：

```python
ocr = PaddleOCR(
    det_model_dir='./models/det/',
    rec_model_dir='./models/rec/',
    cls_model_dir='./models/cls/'
)
```

### Q5: 内存不足 (OOM) / 系统卡死（✅ 已解决）

**症状**:

```
MemoryError
```

或进程被系统杀死，或系统完全卡死

**⚠️ 已确认问题（v0.2.2 已修复）**:

PaddleOCR 3.x 在 macOS ARM 上默认配置可能占用 **40GB+ 内存**，即使是小图片（< 2KB）也会触发。

---

## 问题根源（经源码分析确认）

PaddleOCR 默认启用 **5 个模型**：
1. PP-OCRv5_server_det（文本检测）- 必需
2. PP-OCRv5_server_rec（文本识别）- 必需
3. **DocOrientationClassify（文档方向分类）** - 可选，默认启用
4. **DocUnwarping / UVDoc（文档弯曲矫正）** - 可选，默认启用，**内存大户**
5. **TextLineOrientation（文本行方向）** - 可选，默认启用

即使只做简单文字识别，也会加载所有 5 个模型，导致 macOS ARM 上内存占用极高。

**相关 GitHub Issues**:
- [#16173 - Apple M4 上 25GB 内存占用](https://github.com/PaddlePaddle/PaddleOCR/issues/16173)
- [#16168 - Apple M4 参数改变导致内存爆炸](https://github.com/PaddlePaddle/PaddleOCR/issues/16168)
- [#11639 - 内存泄漏通用问题](https://github.com/PaddlePaddle/PaddleOCR/issues/11639)
- [#11588 - M3 Pro 无法运行](https://github.com/PaddlePaddle/PaddleOCR/issues/11588)

---

## 推荐解决方案（v0.2.2 已在所有示例和 CLI 中应用）

### 方法 1: 禁用预处理模型（⭐⭐⭐ 推荐）

```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,  # 禁用文档方向分类
    use_doc_unwarping=False,             # 禁用文档弯曲矫正（内存大户）
    use_textline_orientation=False,      # 禁用文本行方向分类
)
```

**优化效果（经实测验证）**:
- **内存占用**: 40GB+ → **0.7GB** (节省 **98.2%**)
- **系统稳定性**: ❌ 卡死 → ✅ **正常运行**
- **内存泄漏**: 10 次循环调用后仅增长 **0.06%**
- **功能影响**: 对常规文字识别无影响，弯曲/旋转文档可能需要预处理

### 方法 2: 进一步优化（可选）

```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_det_limit_side_len=640,  # 减小图片最大边长（默认 960）
    text_recognition_batch_size=1  # 减小批处理大小（默认 6）
)
```

**额外优化**: 内存再降低 10-20%

---

## 使用 CLI 工具的保护机制

```bash
# v0.2.2 CLI 已默认启用内存优化配置
paddleocr-guide scan image.png

# CLI 会自动检查图片大小，防止系统卡死
paddleocr-guide scan large_image.png
# 错误: 文件太大: 19.4MB (限制: 10MB)

# 强制处理（风险自负）
paddleocr-guide scan large_image.png --force
```

---

## 验证优化效果

运行测试脚本验证内存占用：

```bash
pytest tests/test_memory_usage.py -v -s
```

---

## ⚠️ 补充说明：大图片仍需注意

虽然禁用预处理模型后初始化内存大幅降低（40GB → 0.7GB），但在处理**大尺寸图片**时，内存仍可能飙升。

### 实测数据

| 图片尺寸 | 像素数 | 文件大小 | 内存峰值 |
|---------|--------|---------|---------|
| 400x100 | 40K | 1.5KB | 0.7GB ✅ |
| 983x1600 | 1.57M | - | 9.3GB ⚠️ |
| 2000x3254 | 6.5M | 4.3MB | 30GB ❌ |

**结论**：图片越大，内存占用越高（远超理论值，疑似 PaddleOCR 内存管理问题）。

### 推荐做法：预处理大图片

对于大于 1600px 的图片，建议先缩小：

```python
from PIL import Image

def resize_for_ocr(image_path, max_size=1200):
    """
    缩小大图片到适合 OCR 的尺寸

    Args:
        image_path: 图片路径
        max_size: 最大边长（推荐 1200-1600）

    Returns:
        处理后的图片路径
    """
    img = Image.open(image_path)

    # 检查是否需要缩小
    max_dim = max(img.width, img.height)
    if max_dim <= max_size:
        return image_path

    # 计算缩放比例
    scale = max_size / max_dim
    new_size = (int(img.width * scale), int(img.height * scale))

    # 使用高质量重采样
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # 保存临时文件
    temp_path = "/tmp/ocr_resized.png"
    img_resized.save(temp_path)

    return temp_path

# 使用示例
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

# 先缩小图片
processed_image = resize_for_ocr("large_image.png", max_size=1200)

# 再识别
result = ocr.predict(processed_image)
```

**优化效果**：
- 内存占用：30GB → **5-7GB**
- 识别准确率：几乎无影响（文字仍然清晰可读）
- 处理速度：更快

### 为什么缩小后识别效果不变？

OCR 识别的关键是**文字的清晰度**，而不是图片的绝对尺寸。

- ✅ 1200px 的图片，文字仍然足够清晰
- ✅ 书籍封面、文档扫描件、截图等常见场景完全够用
- ⚠️ 仅对极小的文字（< 10px）可能有轻微影响

---

### Q6: 识别结果为空

**可能原因**:

1. 图片路径错误
2. 图片格式不支持
3. 图片质量太差
4. 检测阈值过高

**解决**:

```python
import os
from PIL import Image

# 1. 检查图片路径
print(os.path.exists('your_image.png'))

# 2. 检查图片信息
img = Image.open('your_image.png')
print(f"尺寸: {img.size}, 模式: {img.mode}")

# 3. 降低检测阈值
ocr = PaddleOCR(
    det_db_thresh=0.1,      # 降低检测阈值
    det_db_box_thresh=0.3   # 降低文本框阈值
)
```

### Q7: 编码错误

**症状**:

```
UnicodeDecodeError: 'gbk' codec can't decode byte
```

**解决**:

```python
# 确保使用 UTF-8 编码保存结果
with open('result.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
```

---

## macOS 特有问题

### Q8: Apple Silicon 上 PaddleOCR-VL 报错

**症状**:

```
RuntimeError: Unsupported platform
ValueError: Image features and image tokens do not match
```

**原因**: PaddleOCR-VL **不支持** ARM 架构

**解决**:

使用 PP-OCRv5 替代：

```python
from paddleocr import PaddleOCR

# 这个在 M1/M2/M3 上正常工作
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('image.png', cls=True)
```

### Q9: "illegal instruction" 错误

**原因**: 安装了 x86 版本的包

**解决**:

```bash
# 完全卸载
pip uninstall paddlepaddle paddleocr numpy opencv-python

# 重新安装（确保使用 ARM 版本）
pip install paddlepaddle paddleocr
```

### Q10: libiomp5.dylib 冲突

**症状**:

```
OMP: Error #15: Initializing libiomp5.dylib, but found libiomp5.dylib already initialized.
```

**解决**:

```python
# 在代码开头添加
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# 然后再导入 paddleocr
from paddleocr import PaddleOCR
```

### Q11: 无 GPU 加速

**现状**: macOS 不支持 CUDA，PaddlePaddle 也暂不支持 Apple MPS

**解决**:

```python
# 确保使用 CPU 模式
ocr = PaddleOCR(use_gpu=False)

# 开启 MKLDNN 加速（CPU 优化）
ocr = PaddleOCR(enable_mkldnn=True)
```

---

## 识别效果问题

### Q12: 识别准确率不高

**优化方法**:

```python
# 1. 增大输入图片尺寸
ocr = PaddleOCR(det_limit_side_len=1280)  # 默认 960

# 2. 启用方向分类
ocr = PaddleOCR(use_angle_cls=True)

# 3. 图片预处理
import cv2

def preprocess_image(img_path):
    img = cv2.imread(img_path)

    # 转灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 去噪
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

    return denoised

img = preprocess_image('noisy_image.png')
result = ocr.ocr(img, cls=True)
```

### Q13: 倾斜文字识别不好

**解决**:

```python
# 启用方向分类器
ocr = PaddleOCR(use_angle_cls=True)
result = ocr.ocr('tilted_image.png', cls=True)
```

### Q14: 小文字识别不清

**解决**:

```python
# 增大检测输入尺寸
ocr = PaddleOCR(det_limit_side_len=1920)

# 或先放大图片
from PIL import Image

img = Image.open('small_text.png')
img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
img.save('enlarged.png')

result = ocr.ocr('enlarged.png', cls=True)
```

### Q15: 竖排文字识别

**解决**:

```python
# 启用方向分类
ocr = PaddleOCR(use_angle_cls=True)

# 或手动旋转图片
from PIL import Image

img = Image.open('vertical_text.png')
img = img.rotate(90, expand=True)
result = ocr.ocr(img, cls=True)
```

---

## 性能优化

### Q16: CPU 推理太慢

**优化方法**:

```python
# 1. 启用 MKLDNN 加速
ocr = PaddleOCR(enable_mkldnn=True, cpu_threads=4)

# 2. 减小输入尺寸
ocr = PaddleOCR(det_limit_side_len=640)

# 3. 关闭不需要的功能
ocr = PaddleOCR(use_angle_cls=False)  # 如果文字都是正向的

# 4. 复用模型实例
ocr = PaddleOCR()  # 只初始化一次
for img in images:
    result = ocr.ocr(img)  # 多次调用
```

### Q17: GPU 没有被使用

**检查方法**:

```python
import paddle
print(f"CUDA 是否可用: {paddle.device.is_compiled_with_cuda()}")
print(f"当前设备: {paddle.device.get_device()}")
```

**解决**:

```python
# 强制使用 GPU
ocr = PaddleOCR(use_gpu=True, gpu_mem=500)
```

### Q18: 批量处理优化

```python
from paddleocr import PaddleOCR
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

def process_image(img_path):
    result = ocr.ocr(str(img_path), cls=True)
    return img_path.name, result

# 单线程顺序处理（推荐，避免内存问题）
images = list(Path('images/').glob('*.png'))
for img_path in images:
    name, result = process_image(img_path)
    print(f"完成: {name}")
```

---

## 模型相关问题

### Q19: 如何使用自定义模型？

```python
ocr = PaddleOCR(
    det_model_dir='./custom_models/det/',
    rec_model_dir='./custom_models/rec/',
    cls_model_dir='./custom_models/cls/',
    rec_char_dict_path='./custom_dict.txt'
)
```

### Q20: 如何切换模型下载源？

```bash
# 方法 1: 环境变量
export PADDLE_PDX_MODEL_SOURCE=BOS

# 方法 2: 代码中设置
import os
os.environ['PADDLE_PDX_MODEL_SOURCE'] = 'HuggingFace'
```

### Q21: 模型文件在哪里？

默认下载位置：`~/.paddleocr/`

```bash
# 查看已下载的模型
ls -la ~/.paddleocr/
```

---

## 获取更多帮助

如果以上方案无法解决你的问题：

1. 检查 [PaddleOCR GitHub Issues](https://github.com/PaddlePaddle/PaddleOCR/issues)

2. 提交新 Issue 时请包含：
   - 操作系统和版本
   - Python 版本
   - PaddleOCR 版本
   - 完整错误信息
   - 最小复现代码

3. 社区资源：
   - [PaddleOCR 官方文档](https://paddleocr.ai/)
   - [飞桨社区](https://www.paddlepaddle.org.cn/)

---

## 下一步

- [安装指南](installation.md)
- [模型选择指南](model_comparison.md)
- [示例代码](../../examples/)
