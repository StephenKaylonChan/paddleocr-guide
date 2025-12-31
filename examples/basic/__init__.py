# -*- coding: utf-8 -*-
"""
基础 OCR 示例模块
Basic OCR Examples Module

本模块包含 PaddleOCR 的基础使用示例：
- simple_ocr: 简单 OCR 识别 (01_simple_ocr.py)
- batch_ocr: 批量图片处理 (02_batch_ocr.py)
- multilingual: 多语言识别 (03_multilingual.py)

使用方法:
    from examples.basic import simple_ocr
    from examples.basic.simple_ocr import SimpleOCR, OCRResult
"""

import importlib.util
import sys
from pathlib import Path

# 当前目录
_CURRENT_DIR = Path(__file__).parent


def _import_module(filename: str, module_name: str):
    """
    动态导入带数字前缀的模块

    注意：Python 3.12+ 的 dataclass 装饰器需要模块在 sys.modules 中
    正确注册，因此我们需要在 exec_module 之前设置模块。

    Args:
        filename: 文件名 (如 "01_simple_ocr.py")
        module_name: 模块别名 (如 "simple_ocr")

    Returns:
        导入的模块对象
    """
    full_module_name = f"examples.basic.{module_name}"

    spec = importlib.util.spec_from_file_location(
        full_module_name,  # 使用完整模块名
        _CURRENT_DIR / filename,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载模块: {filename}")

    module = importlib.util.module_from_spec(spec)

    # 关键：在 exec_module 之前注册到 sys.modules
    # 这样 dataclass 装饰器才能正确解析模块
    sys.modules[full_module_name] = module

    spec.loader.exec_module(module)
    return module


# 导入模块并创建别名
simple_ocr = _import_module("01_simple_ocr.py", "simple_ocr")
batch_ocr = _import_module("02_batch_ocr.py", "batch_ocr")
multilingual = _import_module("03_multilingual.py", "multilingual")

__all__ = [
    "simple_ocr",
    "batch_ocr",
    "multilingual",
]
