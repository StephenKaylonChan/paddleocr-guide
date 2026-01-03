# 最佳实践汇总

> PaddleOCR 开发的推荐做法和代码规范

本文档汇总了 PaddleOCR 开发中的最佳实践，帮助你编写高质量、可维护的代码。

---

## 目录

- [一、代码组织](#一代码组织)
- [二、性能最佳实践](#二性能最佳实践)
- [三、准确率最佳实践](#三准确率最佳实践)
- [四、生产环境建议](#四生产环境建议)

---

## 一、代码组织

### 1.1 使用上下文管理器

**❌ 不推荐**: 手动管理资源

```python
from paddleocr import PaddleOCR

# 初始化
ocr = PaddleOCR(lang='ch')

# 识别
result = ocr.predict('test.png')

# 问题：OCR 实例没有被释放，可能导致内存泄漏
```

**✅ 推荐**: 使用上下文管理器

```python
from examples._common import OCRContextManager

# 自动资源管理
with OCRContextManager(lang='ch') as ocr:
    result = ocr.predict('test.png')
    # 处理结果...

# OCR 实例已自动释放
```

**优势**:
- 自动释放资源（内存、GPU 显存）
- 异常安全（即使出错也会释放资源）
- 代码更简洁

---

### 1.2 异常处理

**❌ 不推荐**: 忽略异常

```python
result = ocr.predict('test.png')  # 如果文件不存在会崩溃
```

**✅ 推荐**: 捕获并处理异常

```python
from examples._common import (
    OCRException,
    OCRFileNotFoundError,
    OCRProcessError,
    get_logger,
)

logger = get_logger(__name__)

try:
    result = ocr.predict('test.png')
except OCRFileNotFoundError as e:
    logger.error(f"文件不存在: {e}")
    # 处理文件不存在的情况...
except OCRProcessError as e:
    logger.error(f"识别失败: {e}")
    # 处理识别失败的情况...
except OCRException as e:
    logger.error(f"OCR 错误: {e}")
    # 处理其他 OCR 错误...
except Exception as e:
    logger.error(f"未知错误: {e}")
    # 处理未知错误...
```

**异常层次结构**:

```
OCRException（基类）
├── OCRInitError（初始化错误）
├── OCRFileNotFoundError（文件不存在）
├── OCRConfigError（配置错误）
├── OCRProcessError（处理错误）
├── OCROutputError（输出错误）
└── OCRPlatformError（平台错误）
```

**参考**: [错误代码手册](error_codes.md)

---

### 1.3 日志记录

**❌ 不推荐**: 使用 print()

```python
print("开始识别...")
result = ocr.predict('test.png')
print("识别完成")
```

**✅ 推荐**: 使用 logging

```python
from examples._common import setup_logging, get_logger

# 配置日志（通常在主函数开头）
setup_logging(level='INFO')

# 获取 logger
logger = get_logger(__name__)

# 记录日志
logger.info("开始识别...")
result = ocr.predict('test.png')
logger.info("识别完成")
```

**日志级别**:

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 调试信息 | `logger.debug("OCR 参数: {params}")` |
| INFO | 一般信息 | `logger.info("处理完成")` |
| WARNING | 警告信息 | `logger.warning("图片质量较低")` |
| ERROR | 错误信息 | `logger.error("识别失败")` |
| CRITICAL | 严重错误 | `logger.critical("系统崩溃")` |

**进阶用法**:

```python
from examples._common import ProgressLogger

# 进度日志（批量处理）
with ProgressLogger(total=100, desc="处理图片") as progress:
    for i in range(100):
        # 处理图片...
        progress.update(1)  # 更新进度
```

---

### 1.4 类型提示

**❌ 不推荐**: 无类型提示

```python
def process_image(path, lang):
    ocr = PaddleOCR(lang=lang)
    return ocr.predict(path)
```

**✅ 推荐**: 完整的类型提示

```python
from __future__ import annotations
from typing import Any

def process_image(path: str, lang: str = 'ch') -> list[Any]:
    """
    处理图片

    Args:
        path: 图片路径
        lang: 语言代码，默认 'ch'

    Returns:
        list: 识别结果列表
    """
    ocr = PaddleOCR(lang=lang)
    return ocr.predict(path)
```

**优势**:
- 提高代码可读性
- IDE 自动补全和类型检查
- 减少运行时错误

---

### 1.5 配置管理

**❌ 不推荐**: 硬编码配置

```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
```

**✅ 推荐**: 使用配置常量

```python
from examples._common import DEFAULT_OCR_CONFIG

# 使用默认配置（已包含 macOS 优化）
ocr = PaddleOCR(**DEFAULT_OCR_CONFIG)

# 自定义配置
custom_config = DEFAULT_OCR_CONFIG.copy()
custom_config['use_gpu'] = True
custom_config['rec_batch_num'] = 10

ocr = PaddleOCR(**custom_config)
```

**可用配置**:

```python
from examples._common import (
    DEFAULT_OCR_CONFIG,           # OCR 默认配置
    DEFAULT_STRUCTURE_CONFIG,     # 文档分析默认配置
    OCRDefaults,                  # OCR 默认值类
    StructureDefaults,            # 文档分析默认值类
)

# 查看默认配置
print(DEFAULT_OCR_CONFIG)
# {
#     'lang': 'ch',
#     'use_doc_orientation_classify': False,
#     'use_doc_unwarping': False,
#     'use_textline_orientation': False,
# }
```

---

### 1.6 文件操作

**❌ 不推荐**: 不检查文件是否存在

```python
result = ocr.predict('test.png')  # 可能失败
```

**✅ 推荐**: 使用工具函数

```python
from examples._common import validate_file_exists, ensure_directory

# 验证文件存在
validate_file_exists('test.png')  # 如果不存在会抛出 OCRFileNotFoundError

# 确保目录存在
ensure_directory('output/')  # 自动创建目录（如果不存在）

# 识别
result = ocr.predict('test.png')
```

---

## 二、性能最佳实践

### 2.1 内存管理

#### macOS 用户必读

**❗ 关键**: macOS ARM 用户**必须**添加这 3 个参数，否则内存占用 40GB+

```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,  # 必须
    use_doc_unwarping=False,             # 必须
    use_textline_orientation=False,      # 必须
)
```

**效果**: 内存从 40GB 降至 **0.7GB**（节省 98.2%）

**参考**: [性能优化 - 内存优化](performance.md#11-macos-arm-内存问题)

---

#### 大图片预处理

**❌ 不推荐**: 直接识别大图片

```python
result = ocr.predict('large_image.png')  # 2000x3254, 可能占用 30GB 内存
```

**✅ 推荐**: 预先缩小图片

```python
from examples._common import resize_image_for_ocr

# 自动缩小到 1200px
resized_path = resize_image_for_ocr('large_image.png', max_size=1200)

# 识别缩小后的图片（内存降至 5-7GB）
result = ocr.predict(resized_path)
```

**推荐尺寸**:
- 普通文档: 1200px
- 高清需求: 1600px
- 速度优先: 800-1000px

---

#### 批量处理内存管理

**❌ 不推荐**: 无内存管理

```python
for img in images:
    result = ocr.predict(img)  # 内存持续增长
```

**✅ 推荐**: 分批处理 + 垃圾回收

```python
import gc

batch_size = 20

for i in range(0, len(images), batch_size):
    batch = images[i:i + batch_size]

    for img in batch:
        result = ocr.predict(img)
        # 处理结果...

    # 每批次后垃圾回收
    gc.collect()
```

**更好的方案**: 使用公共模块

```python
from examples._common import batch_process

results = batch_process(
    files=images,
    processor_fn=lambda ocr, path: ocr.predict(path),
    batch_size=20,          # 垃圾回收间隔
    chunk_size=100,         # 重新初始化间隔
    memory_threshold=2000,  # 2GB 内存阈值
)
```

---

### 2.2 速度优化

#### GPU 加速

**✅ 推荐**: 有 GPU 的情况下启用

```python
ocr = PaddleOCR(
    lang='ch',
    use_gpu=True,                        # 启用 GPU
    gpu_mem=8000,                        # GPU 内存限制（MB）
    rec_batch_num=10,                    # 批处理大小
    use_doc_orientation_classify=False,  # macOS 优化
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
```

**加速效果**: GPU 比 CPU 快 **10-20 倍**

**注意**: macOS ARM (M1/M2/M3) 不支持 CUDA

---

#### 模型选择

| 场景 | 推荐模型 | 速度 | 准确率 |
|------|---------|------|--------|
| 开发测试 | Mobile | 极快 | 94% |
| 生产环境 | 默认 | 快 | 96% |
| 高准确率 | Server | 中 | 98%+ |

```python
# Server 模型（高准确率）
ocr = PaddleOCR(
    lang='ch',
    det_model_dir='ch_PP_OCRv5_server_det',
    rec_model_dir='ch_PP_OCRv5_server_rec',
    # ...
)
```

---

## 三、准确率最佳实践

### 3.1 图片预处理

**✅ 推荐**: 预处理低质量图片

```python
from PIL import Image, ImageEnhance

def enhance_image(image_path: str) -> str:
    """图片增强"""
    img = Image.open(image_path)

    # 锐化
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)

    # 对比度增强
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    output_path = '/tmp/enhanced.png'
    img.save(output_path)
    return output_path

# 使用
enhanced = enhance_image('blurry.png')
result = ocr.predict(enhanced)
```

**效果**: 模糊图片准确率从 85% 提升至 92%

---

### 3.2 参数调优

**✅ 推荐**: 针对特定场景调优

```python
# 低质量图片（提高检测灵敏度）
ocr = PaddleOCR(
    lang='ch',
    det_db_thresh=0.2,       # 降低检测阈值（默认 0.3）
    drop_score=0.3,          # 降低置信度阈值（默认 0.5）
    det_limit_side_len=1600, # 提高分辨率（默认 960）
    # ...
)
```

**关键参数**:

| 参数 | 说明 | 调优建议 |
|------|------|---------|
| `det_limit_side_len` | 检测图片最大边长 | 大图片设为 1600-2000 |
| `det_db_thresh` | 检测阈值 | 低质量降至 0.2 |
| `drop_score` | 置信度阈值 | 低质量降至 0.3 |

---

### 3.3 语言选择

**✅ 推荐**: 使用正确的语言代码

```python
from examples._common import normalize_language, is_supported_language

# 验证语言
lang = 'chinese'
if not is_supported_language(lang):
    # 尝试规范化
    lang = normalize_language(lang)  # 'chinese' → 'ch'

ocr = PaddleOCR(lang=lang)
```

**常用语言代码**:

| 语言 | 代码 | 别名 |
|------|------|------|
| 中文 | `ch` | `chinese`, `zh`, `中文` |
| 英文 | `en` | `english` |
| 日文 | `japan` | `ja`, `japanese` |
| 韩文 | `korean` | `ko`, `kr` |

---

## 四、生产环境建议

### 4.1 错误处理

**✅ 推荐**: 完整的错误处理策略

```python
from examples._common import (
    OCRContextManager,
    OCRException,
    get_logger,
)

logger = get_logger(__name__)

def safe_ocr(image_path: str, max_retries: int = 3) -> list | None:
    """
    安全的 OCR 识别（带重试）

    Args:
        image_path: 图片路径
        max_retries: 最大重试次数

    Returns:
        list | None: 识别结果，失败返回 None
    """
    for attempt in range(max_retries):
        try:
            with OCRContextManager(lang='ch') as ocr:
                result = ocr.predict(image_path)
                return list(result)

        except OCRException as e:
            logger.warning(
                f"OCR 失败 (尝试 {attempt + 1}/{max_retries}): {e}"
            )
            if attempt == max_retries - 1:
                logger.error(f"OCR 最终失败: {image_path}")
                return None

        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None

    return None
```

---

### 4.2 监控和日志

**✅ 推荐**: 记录关键指标

```python
import time
import psutil
from examples._common import get_logger

logger = get_logger(__name__)
process = psutil.Process()

def monitor_ocr(image_path: str):
    """监控 OCR 性能"""
    start_time = time.time()
    start_mem = process.memory_info().rss / 1024 / 1024

    # 识别
    result = ocr.predict(image_path)

    # 计算指标
    elapsed = time.time() - start_time
    end_mem = process.memory_info().rss / 1024 / 1024
    mem_used = end_mem - start_mem

    # 记录日志
    logger.info(
        f"OCR 完成: {image_path} | "
        f"耗时: {elapsed:.2f}s | "
        f"内存: {mem_used:.1f} MB"
    )

    return result
```

---

### 4.3 资源限制

**✅ 推荐**: 设置资源限制

```python
import resource

# 限制最大内存（4GB）
max_memory = 4 * 1024 * 1024 * 1024  # 4GB in bytes
resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))

# 限制 CPU 时间（10 分钟）
max_cpu_time = 10 * 60  # 600 seconds
resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_time, max_cpu_time))
```

---

### 4.4 并发处理

**✅ 推荐**: 使用多进程（而非多线程）

```python
from multiprocessing import Pool
from functools import partial

def process_image(image_path: str, lang: str = 'ch'):
    """处理单张图片"""
    with OCRContextManager(lang=lang) as ocr:
        return ocr.predict(image_path)

# 多进程批量处理
with Pool(processes=4) as pool:
    results = pool.map(process_image, image_paths)
```

**注意**:
- Python GIL 限制，OCR 推荐使用**多进程**而非多线程
- 进程数 = CPU 核心数 - 1（保留一个核心给系统）

---

### 4.5 缓存策略

**✅ 推荐**: 缓存识别结果

```python
import hashlib
import json
from pathlib import Path

class OCRCache:
    """OCR 结果缓存"""

    def __init__(self, cache_dir: str = '.ocr_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, image_path: str) -> str:
        """生成缓存键（文件 MD5）"""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def get(self, image_path: str) -> list | None:
        """获取缓存"""
        key = self.get_cache_key(image_path)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None

    def set(self, image_path: str, result: list) -> None:
        """设置缓存"""
        key = self.get_cache_key(image_path)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)

# 使用
cache = OCRCache()

def cached_ocr(image_path: str):
    """带缓存的 OCR"""
    # 检查缓存
    cached_result = cache.get(image_path)
    if cached_result:
        return cached_result

    # 识别
    result = ocr.predict(image_path)

    # 保存缓存
    cache.set(image_path, result)

    return result
```

---

## 总结：最佳实践清单

### ✅ 必须遵守

- [ ] macOS 用户添加 3 个禁用参数
- [ ] 使用上下文管理器管理资源
- [ ] 添加异常处理（捕获 OCRException）
- [ ] 使用 logging 代替 print()
- [ ] 验证文件存在性
- [ ] 大图片（>1600px）预先缩小

### ✅ 强烈推荐

- [ ] 使用类型提示
- [ ] 批量处理时分批 + 垃圾回收
- [ ] 启用 GPU（如果可用）
- [ ] 选择合适的模型
- [ ] 低质量图片预处理
- [ ] 记录性能指标

### ✅ 生产环境

- [ ] 实现重试机制
- [ ] 设置资源限制
- [ ] 使用多进程（而非多线程）
- [ ] 缓存识别结果
- [ ] 监控和告警

---

## 代码模板

### 完整示例（生产级）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产级 OCR 示例
Production-Ready OCR Example
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from examples._common import (
    OCRContextManager,
    OCRException,
    setup_logging,
    get_logger,
    validate_file_exists,
    resize_image_for_ocr,
)

# 配置日志
setup_logging(level='INFO')
logger = get_logger(__name__)


def process_image(
    image_path: str,
    max_retries: int = 3,
) -> list[Any] | None:
    """
    处理单张图片（生产级）

    Args:
        image_path: 图片路径
        max_retries: 最大重试次数

    Returns:
        list | None: 识别结果，失败返回 None
    """
    # 验证文件
    try:
        validate_file_exists(image_path)
    except OCRException as e:
        logger.error(f"文件验证失败: {e}")
        return None

    # 预处理大图片
    processed_path = resize_image_for_ocr(image_path, max_size=1200)

    # 重试识别
    for attempt in range(max_retries):
        try:
            start_time = time.time()

            # 使用上下文管理器
            with OCRContextManager(lang='ch') as ocr:
                result = ocr.predict(processed_path)

            elapsed = time.time() - start_time
            logger.info(
                f"✓ {Path(image_path).name} | "
                f"耗时: {elapsed:.2f}s"
            )

            return list(result)

        except OCRException as e:
            logger.warning(
                f"识别失败 (尝试 {attempt + 1}/{max_retries}): {e}"
            )

            if attempt == max_retries - 1:
                logger.error(f"最终失败: {image_path}")
                return None

    return None


def main():
    """主函数"""
    image_path = 'test.png'

    # 处理图片
    result = process_image(image_path)

    if result:
        logger.info("识别成功")
        # 处理结果...
    else:
        logger.error("识别失败")


if __name__ == '__main__':
    main()
```

---

## 参考资源

- [快速入门](quickstart.md)
- [性能优化](performance.md)
- [实际案例](case_studies.md)
- [错误代码手册](error_codes.md)
- [示例代码](../../examples/)

---

**上次更新**: 2026-01-03
**版本**: v0.3.0
