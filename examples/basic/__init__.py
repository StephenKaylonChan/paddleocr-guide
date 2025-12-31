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
    """动态导入带数字前缀的模块"""
    spec = importlib.util.spec_from_file_location(
        module_name,
        _CURRENT_DIR / filename,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载模块: {filename}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[f"examples.basic.{module_name}"] = module
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
