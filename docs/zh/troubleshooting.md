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

### Q5: 内存不足 (OOM)

**症状**:

```
MemoryError
```

或进程被系统杀死

**解决**:

```python
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    det_limit_side_len=640,  # 减小图片最大边长（默认 960）
    rec_batch_num=1          # 减小批处理大小
)
```

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
