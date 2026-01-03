# 错误代码手册

> PaddleOCR 完整错误代码参考和解决方案

本手册提供项目中所有错误代码的详细说明、原因分析和解决方案。

---

## 错误代码体系

项目使用 6 类错误代码（E1xx - E6xx）：

| 代码范围 | 错误类型 | 说明 |
|---------|---------|------|
| **E1xx** | **初始化错误** | OCR 引擎、模型加载失败 |
| **E2xx** | **处理错误** | 图像识别、文档解析失败 |
| **E3xx** | **文件错误** | 文件不存在、格式不支持 |
| **E4xx** | **配置错误** | 参数无效、语言不支持 |
| **E5xx** | **输出错误** | 结果保存、权限不足 |
| **E6xx** | **平台错误** | 平台不支持、资源不足 |

---

## 目录

- [E1xx - 初始化错误](#e1xx---初始化错误)
- [E2xx - 处理错误](#e2xx---处理错误)
- [E3xx - 文件错误](#e3xx---文件错误)
- [E4xx - 配置错误](#e4xx---配置错误)
- [E5xx - 输出错误](#e5xx---输出错误)
- [E6xx - 平台错误](#e6xx---平台错误)

---

## E1xx - 初始化错误

### E101: OCR 引擎初始化失败

**完整错误信息**:
```
[E101] OCR 引擎初始化失败
```

**原因**:
1. PaddleOCR 或 PaddlePaddle 未安装
2. 模型下载失败或损坏
3. 网络连接问题（无法下载模型）
4. 内存不足无法加载模型
5. 语言代码无效

**解决方案**:

#### 方案 1：检查依赖安装

```bash
# 检查是否安装 PaddleOCR
pip show paddleocr

# 如果未安装
pip install paddleocr
```

#### 方案 2：检查网络连接

```bash
# 测试是否能访问模型下载地址
curl -I https://paddleocr.bj.bcebos.com/

# 如果无法访问，配置代理
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

#### 方案 3：手动下载模型

```bash
# 下载模型到本地
wget https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/ch_PP-OCRv5_det_infer.tar
wget https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/ch_PP-OCRv5_rec_infer.tar

# 解压
tar -xf ch_PP-OCRv5_det_infer.tar
tar -xf ch_PP-OCRv5_rec_infer.tar

# 指定本地模型路径
ocr = PaddleOCR(
    lang='ch',
    det_model_dir='./ch_PP-OCRv5_det_infer',
    rec_model_dir='./ch_PP-OCRv5_rec_infer',
)
```

#### 方案 4：清理缓存重试

```bash
# 删除模型缓存
rm -rf ~/.paddleocr/

# 重新运行
python your_script.py
```

**代码示例**:

```python
from examples._common import OCRInitError

try:
    ocr = PaddleOCR(lang='ch')
except Exception as e:
    raise OCRInitError(
        "OCR 引擎初始化失败",
        error_code="E101",
        details={"original_error": str(e)}
    )
```

---

### E102: 模型加载失败

**原因**:
- 模型文件损坏
- 模型路径错误
- 模型版本不兼容

**解决方案**:

```python
# 检查模型文件是否存在
from pathlib import Path

model_path = Path('~/.paddleocr/whl/det/ch/ch_PP-OCRv5_det_infer/')
if not model_path.exists():
    print("模型文件不存在，将自动下载...")

# 验证模型完整性
import hashlib

def verify_model(file_path: str, expected_hash: str) -> bool:
    """验证模型文件 MD5"""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash == expected_hash
```

---

### E103: 依赖缺失

**原因**:
- PaddlePaddle 未安装
- 缺少图像处理库（Pillow, opencv-python）
- Python 版本不兼容

**解决方案**:

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 安装所有依赖
pip install -r requirements.txt

# 或手动安装
pip install paddlepaddle paddleocr pillow opencv-python
```

---

## E2xx - 处理错误

### E201: 图像识别失败

**完整错误信息**:
```
[E201] OCR 处理失败
```

**原因**:
1. 图像格式不支持（如 WEBP, TIFF）
2. 图像损坏或不完整
3. 图像尺寸过大导致内存溢出
4. 图像尺寸过小（< 10x10）
5. 识别超时

**解决方案**:

#### 方案 1：检查图像格式

```python
from PIL import Image

def check_image(image_path: str) -> bool:
    """检查图像是否有效"""
    try:
        img = Image.open(image_path)
        img.verify()  # 验证图像完整性
        return True
    except Exception as e:
        print(f"图像无效: {e}")
        return False

# 转换为支持的格式
def convert_to_png(image_path: str) -> str:
    """转换图像为 PNG"""
    img = Image.open(image_path)
    output_path = image_path.rsplit('.', 1)[0] + '.png'
    img.save(output_path, 'PNG')
    return output_path
```

#### 方案 2：检查图像尺寸

```python
from examples._common import get_file_stats, resize_image_for_ocr

# 检查尺寸
stats = get_file_stats('test.png')
print(f"图像尺寸: {stats['dimensions']}")

# 如果过大，缩小
if max(stats['dimensions']) > 2000:
    resized = resize_image_for_ocr('test.png', max_size=1200)
    result = ocr.predict(resized)
```

#### 方案 3：增加超时时间

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("识别超时")

# 设置 60 秒超时
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

try:
    result = ocr.predict('large_image.png')
    signal.alarm(0)  # 取消超时
except TimeoutError:
    print("识别超时，请尝试缩小图像")
```

**代码示例**:

```python
from examples._common import OCRProcessError

try:
    result = ocr.predict('test.png')
except Exception as e:
    raise OCRProcessError(
        "图像识别失败",
        image_path='test.png',
        error_code="E201",
        details={"original_error": str(e)}
    )
```

---

### E202: 文档解析失败

**原因**:
- PDF 文件损坏
- PDF 加密或受保护
- PDF 页数过多

**解决方案**:

```python
import PyPDF2

def check_pdf(pdf_path: str) -> tuple[bool, str]:
    """检查 PDF 是否可读"""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # 检查是否加密
            if reader.is_encrypted:
                return False, "PDF 已加密"

            # 检查页数
            page_count = len(reader.pages)
            if page_count > 1000:
                return False, f"PDF 页数过多: {page_count} 页"

            return True, ""

    except Exception as e:
        return False, str(e)

# 使用
valid, error = check_pdf('document.pdf')
if not valid:
    print(f"PDF 无效: {error}")
```

---

### E203: 表格识别失败

**原因**:
- 表格线条不清晰
- 复杂嵌套表格
- 表格跨页

**解决方案**:

```python
# 预处理表格图像
from PIL import Image, ImageEnhance

def enhance_table(image_path: str) -> str:
    """增强表格图像"""
    img = Image.open(image_path)

    # 转为灰度
    img = img.convert('L')

    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    output_path = '/tmp/enhanced_table.png'
    img.save(output_path)
    return output_path
```

---

### E204: 公式识别失败

**原因**:
- 公式图像不清晰
- 手写公式识别困难
- 复杂公式结构

**解决方案**:

```python
# 使用 PP-StructureV3（支持公式识别）
from paddleocr import PPStructureV3

engine = PPStructureV3(lang='ch')
result = engine.predict('formula.png')

# 提取 LaTeX
for res in result:
    data = res.json
    if 'latex' in data:
        print(f"LaTeX: {data['latex']}")
```

---

## E3xx - 文件错误

### E301: 文件不存在

**完整错误信息**:
```
[E301] 文件不存在
```

**原因**:
- 文件路径错误
- 文件已被删除
- 权限问题无法访问

**解决方案**:

#### 方案 1：验证路径

```python
from pathlib import Path

image_path = 'test.png'

# 检查文件是否存在
if not Path(image_path).exists():
    print(f"文件不存在: {image_path}")

    # 检查当前目录
    print(f"当前目录: {Path.cwd()}")
    print(f"目录内容: {list(Path.cwd().iterdir())}")

# 或使用公共模块
from examples._common import validate_file_exists

try:
    validate_file_exists(image_path)
except OCRFileNotFoundError as e:
    print(f"错误: {e}")
```

#### 方案 2：使用绝对路径

```python
from pathlib import Path

# 相对路径 → 绝对路径
image_path = Path('test.png').resolve()
print(f"绝对路径: {image_path}")

# 检查
if image_path.exists():
    result = ocr.predict(str(image_path))
```

**代码示例**:

```python
from examples._common import OCRFileNotFoundError

if not Path(file_path).exists():
    raise OCRFileNotFoundError(
        f"图像文件不存在: {file_path}",
        file_path=file_path,
        error_code="E301"
    )
```

---

### E302: 文件格式不支持

**原因**:
- 文件扩展名不正确
- 文件实际格式与扩展名不符

**解决方案**:

```python
from examples._common import (
    is_supported_image,
    is_supported_document,
    ALL_SUPPORTED_EXTENSIONS,
)

# 检查格式
if not is_supported_image('test.webp'):
    print("不支持的图像格式")
    print(f"支持的格式: {ALL_SUPPORTED_EXTENSIONS}")

# 转换格式
from PIL import Image

def convert_to_supported_format(file_path: str) -> str:
    """转换为支持的格式"""
    img = Image.open(file_path)
    output_path = file_path.rsplit('.', 1)[0] + '.png'
    img.save(output_path, 'PNG')
    return output_path
```

---

### E303: 文件损坏

**原因**:
- 文件下载不完整
- 文件传输过程损坏
- 存储设备错误

**解决方案**:

```python
from PIL import Image

def verify_image(image_path: str) -> bool:
    """验证图像完整性"""
    try:
        img = Image.open(image_path)
        img.verify()  # 验证图像数据
        img = Image.open(image_path)  # 重新打开（verify 后无法继续使用）
        img.load()  # 尝试加载像素数据
        return True
    except Exception as e:
        print(f"图像损坏: {e}")
        return False
```

---

## E4xx - 配置错误

### E401: 参数无效

**完整错误信息**:
```
[E401] 配置参数无效
```

**原因**:
- 参数类型错误
- 参数值超出范围
- 参数组合冲突

**解决方案**:

```python
from examples._common import OCRDefaults, DEFAULT_OCR_CONFIG

# 使用默认配置
config = DEFAULT_OCR_CONFIG.copy()

# 验证参数
if config.get('rec_batch_num', 0) < 1:
    raise OCRConfigError(
        "rec_batch_num 必须 >= 1",
        error_code="E401",
        details={"rec_batch_num": config['rec_batch_num']}
    )

# 应用配置
ocr = PaddleOCR(**config)
```

---

### E402: 语言不支持

**原因**:
- 语言代码错误
- 该语言模型未安装

**解决方案**:

```python
from examples._common import (
    SUPPORTED_LANGUAGES,
    is_supported_language,
    normalize_language,
)

# 检查语言
lang = 'chinese'
if not is_supported_language(lang):
    # 尝试规范化
    lang = normalize_language(lang)  # 'chinese' → 'ch'

# 如果仍不支持
if not is_supported_language(lang):
    raise OCRConfigError(
        f"不支持的语言: {lang}",
        error_code="E402",
        details={
            "lang": lang,
            "supported": list(SUPPORTED_LANGUAGES.keys())[:10]
        }
    )

ocr = PaddleOCR(lang=lang)
```

**查看所有支持的语言**:

```bash
paddleocr-guide langs
```

或：

```python
from examples._common import SUPPORTED_LANGUAGES

print(f"支持 {len(SUPPORTED_LANGUAGES)} 种语言:")
for lang in SUPPORTED_LANGUAGES:
    print(f"  - {lang}")
```

---

### E403: 参数冲突

**原因**:
- 同时启用互斥参数
- CPU/GPU 配置冲突

**解决方案**:

```python
# 错误示例
ocr = PaddleOCR(
    use_gpu=True,
    use_cpu=True,  # 冲突！
)

# 正确配置
ocr = PaddleOCR(
    use_gpu=True,   # 只启用 GPU
    gpu_mem=8000,
)
```

---

## E5xx - 输出错误

### E501: 保存失败

**完整错误信息**:
```
[E501] 结果保存失败
```

**原因**:
- 输出目录不存在
- 权限不足
- 磁盘空间不足
- 文件名包含非法字符

**解决方案**:

#### 方案 1：确保目录存在

```python
from examples._common import ensure_directory

# 自动创建目录
output_dir = 'results/'
ensure_directory(output_dir)

# 保存结果
output_path = output_dir + 'result.json'
result.save_to_json(output_path)
```

#### 方案 2：检查权限

```python
import os

output_path = 'results/output.json'

# 检查目录是否可写
output_dir = os.path.dirname(output_path)
if not os.access(output_dir, os.W_OK):
    raise OCROutputError(
        f"无写入权限: {output_dir}",
        output_path=output_path,
        error_code="E502"
    )
```

#### 方案 3：检查磁盘空间

```python
import shutil

def check_disk_space(path: str, required_mb: int = 100) -> bool:
    """检查磁盘空间"""
    stat = shutil.disk_usage(path)
    free_mb = stat.free / 1024 / 1024
    return free_mb >= required_mb

if not check_disk_space('/', required_mb=100):
    raise OCROutputError(
        "磁盘空间不足",
        error_code="E503"
    )
```

**代码示例**:

```python
from examples._common import OCROutputError

try:
    result.save_to_json('output.json')
except Exception as e:
    raise OCROutputError(
        "无法保存结果",
        output_path='output.json',
        error_code="E501",
        details={"original_error": str(e)}
    )
```

---

### E502: 权限不足

**解决方案**:

```bash
# 修改目录权限
chmod 755 results/

# 或使用当前用户有权限的目录
output_dir = '~/ocr_results/'
```

---

### E503: 磁盘空间不足

**解决方案**:

```bash
# 检查磁盘空间
df -h

# 清理空间
rm -rf ~/.paddleocr/cache/
```

---

## E6xx - 平台错误

### E601: 平台不支持

**完整错误信息**:
```
[E601] 当前平台不支持此功能
```

**原因**:
- macOS ARM 不支持 PaddleOCR-VL
- 某些功能仅支持 Linux

**解决方案**:

```python
from examples._common import PLATFORM_INFO, OCRPlatformError

# 检查平台
if PLATFORM_INFO.is_macos_arm:
    if feature == 'paddleocr_vl':
        raise OCRPlatformError(
            "PaddleOCR-VL 不支持 macOS ARM",
            platform_info=PLATFORM_INFO.get_platform_string(),
            feature="PaddleOCR-VL",
            error_code="E601"
        )

# 使用替代方案
if PLATFORM_INFO.is_macos_arm:
    # 使用 PP-OCRv5 替代
    ocr = PaddleOCR(lang='ch')
```

**检查平台兼容性**:

```python
from examples._common import check_platform

info = check_platform()
print(f"平台: {info['platform']}")
print(f"PaddleOCR-VL 支持: {info['supports_vl']}")
```

---

### E602: GPU 不可用

**原因**:
- 没有 NVIDIA GPU
- CUDA 未安装
- CUDA 版本不兼容

**解决方案**:

```python
import paddle

# 检查 CUDA
if paddle.is_compiled_with_cuda():
    print("✓ CUDA 可用")
    print(f"  GPU 数量: {paddle.device.cuda.device_count()}")
else:
    print("✗ CUDA 不可用，将使用 CPU")
    # 禁用 GPU
    ocr = PaddleOCR(lang='ch', use_gpu=False)
```

---

### E603: 内存不足

**原因**:
- macOS ARM 未禁用预处理模型（40GB+ 内存）
- 图片过大
- 批处理未做内存管理

**解决方案**:

#### 方案 1：macOS 优化配置（必须）

```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,  # 必须
    use_doc_unwarping=False,             # 必须
    use_textline_orientation=False,      # 必须
)
```

**效果**: 内存从 40GB 降至 **0.7GB**

#### 方案 2：图片预处理

```python
from examples._common import resize_image_for_ocr

# 缩小大图片
resized = resize_image_for_ocr('large.png', max_size=1200)
result = ocr.predict(resized)
```

#### 方案 3：批处理优化

```python
import gc

for i in range(0, len(images), batch_size):
    batch = images[i:i + batch_size]

    for img in batch:
        result = ocr.predict(img)

    # 强制垃圾回收
    gc.collect()
```

**参考**: [性能优化 - 内存优化](performance.md#一内存优化)

---

## 异常处理最佳实践

### 捕获特定异常

```python
from examples._common import (
    OCRException,
    OCRInitError,
    OCRProcessError,
    OCRFileNotFoundError,
    OCRConfigError,
    OCROutputError,
    OCRPlatformError,
)

try:
    # OCR 操作
    result = ocr.predict('test.png')

except OCRFileNotFoundError as e:
    # 处理文件不存在
    logger.error(f"文件不存在: {e.file_path}")

except OCRProcessError as e:
    # 处理识别失败
    logger.error(f"识别失败: {e.image_path}")

except OCRPlatformError as e:
    # 处理平台不支持
    logger.error(f"平台不支持: {e.feature}")

except OCRException as e:
    # 处理其他 OCR 错误
    logger.error(f"OCR 错误 [{e.error_code}]: {e.message}")
    logger.debug(f"详细信息: {e.details}")

except Exception as e:
    # 处理未知错误
    logger.error(f"未知错误: {e}")
```

---

### 抛出自定义异常

```python
from pathlib import Path
from examples._common import OCRFileNotFoundError, OCRConfigError

# 示例 1：文件不存在
if not Path(image_path).exists():
    raise OCRFileNotFoundError(
        f"图像文件不存在: {image_path}",
        file_path=image_path,
    )

# 示例 2：配置错误
if lang not in SUPPORTED_LANGUAGES:
    raise OCRConfigError(
        f"不支持的语言: {lang}",
        details={
            "lang": lang,
            "supported": list(SUPPORTED_LANGUAGES.keys())
        }
    )
```

---

## 总结：常见错误快速查询

| 错误代码 | 错误类型 | 快速解决方案 |
|---------|---------|-------------|
| **E101** | 初始化失败 | 检查依赖安装、网络连接 |
| **E201** | 识别失败 | 检查图像格式、缩小大图片 |
| **E301** | 文件不存在 | 验证文件路径、使用绝对路径 |
| **E401** | 参数无效 | 使用 DEFAULT_OCR_CONFIG |
| **E402** | 语言不支持 | 使用 normalize_language() |
| **E501** | 保存失败 | 检查目录权限、磁盘空间 |
| **E601** | 平台不支持 | macOS ARM 避免 PaddleOCR-VL |
| **E603** | 内存不足 | macOS 禁用 3 个预处理模型 |

---

## 参考资源

- [快速入门](quickstart.md)
- [性能优化](performance.md)
- [最佳实践](best_practices.md)
- [故障排查](troubleshooting.md)
- [异常类源码](../../examples/_common/exceptions.py)

---

**上次更新**: 2026-01-03
**版本**: v0.3.0
