# -*- coding: utf-8 -*-
"""
PaddleOCR Guide 测试包
PaddleOCR Guide Test Package

测试结构:
    tests/
    ├── __init__.py          # 本文件
    ├── conftest.py          # pytest fixtures
    ├── test_common.py       # 公共模块测试
    ├── test_basic_ocr.py    # 基础 OCR 测试
    ├── test_document.py     # 文档处理测试
    └── test_advanced.py     # 高级功能测试

运行测试:
    pytest tests/ -v
    pytest tests/ -v --cov=examples
    pytest tests/ -v -m "not slow"
"""
