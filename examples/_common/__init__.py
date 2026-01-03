#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 示例公共模块
PaddleOCR Examples Common Module

本模块提供了 PaddleOCR 示例代码的公共基础设施，包括：
- 异常类：统一的异常处理
- 配置常量：语言代码、图片格式、默认参数
- 日志系统：替代 print() 的日志管理
- 基础类：上下文管理器、处理器基类
- 工具函数：文件操作、结果处理

This module provides common infrastructure for PaddleOCR examples:
- Exceptions: Unified error handling
- Config constants: Language codes, image formats, defaults
- Logging: Logging management replacing print()
- Base classes: Context managers, processor base classes
- Utilities: File operations, result processing

使用方式 / Usage:
    >>> from examples._common import (
    ...     OCRContextManager,
    ...     OCRException,
    ...     setup_logging,
    ...     get_logger,
    ... )
    >>>
    >>> # 配置日志
    >>> setup_logging()
    >>> logger = get_logger(__name__)
    >>>
    >>> # 使用上下文管理器
    >>> with OCRContextManager(lang='ch') as ocr:
    ...     result = ocr.predict('image.png')

作者: paddleocr-guide
版本: 0.2.0
API 版本: PaddleOCR 3.x
"""

from __future__ import annotations

# =============================================================================
# 版本信息
# Version Information
# =============================================================================

__version__ = "0.2.0"
__author__ = "paddleocr-guide"


# =============================================================================
# 异常类导出
# Exception Classes Export
# =============================================================================

from .base import (  # 上下文管理器; 基类; 装饰器
    BaseOCRProcessor,
    OCRContextManager,
    OCRResultWrapper,
    StructureContextManager,
    ocr_session,
    require_non_arm_mac,
    structure_session,
)
from .config import (  # 语言配置; 文件格式; 默认配置; 路径配置; 平台信息; 输出格式
    ALL_SUPPORTED_EXTENSIONS,
    DEFAULT_OCR_CONFIG,
    DEFAULT_STRUCTURE_CONFIG,
    LANGUAGE_ALIASES,
    PATH_CONFIG,
    PLATFORM_INFO,
    SUPPORTED_DOCUMENT_EXTENSIONS,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_LANGUAGES,
    OCRDefaults,
    OutputFormat,
    PathConfig,
    PlatformInfo,
    StructureDefaults,
    is_supported_document,
    is_supported_image,
    is_supported_input,
    is_supported_language,
    normalize_language,
)
from .exceptions import (
    OCRConfigError,
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    OCROutputError,
    OCRPlatformError,
    OCRProcessError,
)
from .logging_config import (
    ColoredFormatter,
    LogContext,
    ProgressLogger,
    get_logger,
    setup_logging,
)
from .utils import (  # 文件操作; JSON 操作; 文本处理; 时间和统计; 批处理; 环境
    batch_process,
    clean_text,
    create_summary_report,
    ensure_directory,
    extract_text_only,
    find_images,
    format_file_size,
    format_ocr_result,
    get_env_or_default,
    get_file_stats,
    get_output_path,
    get_timestamp,
    join_texts,
    load_json,
    resize_image_for_ocr,
    save_json,
    set_paddleocr_env,
    validate_file_exists,
)

# =============================================================================
# 配置常量导出
# Configuration Constants Export
# =============================================================================



# =============================================================================
# 日志系统导出
# Logging System Export
# =============================================================================



# =============================================================================
# 基础类导出
# Base Classes Export
# =============================================================================



# =============================================================================
# 工具函数导出
# Utility Functions Export
# =============================================================================



# =============================================================================
# 模块级便捷函数
# Module-level Convenience Functions
# =============================================================================


def quick_ocr(
    image_path: str,
    *,
    lang: str = "ch",
    print_result: bool = True,
) -> list:
    """
    快速 OCR 识别 - 一行代码完成识别

    这是最简单的使用方式，适合快速测试。

    Args:
        image_path: 图片路径
        lang: 语言代码，默认 'ch'
        print_result: 是否打印结果

    Returns:
        list: 识别结果列表

    Example:
        >>> from examples._common import quick_ocr
        >>> result = quick_ocr('test.png')
        >>> # 自动打印结果
    """
    setup_logging()

    with OCRContextManager(lang=lang) as ocr:
        result = ocr.predict(image_path)

        if print_result:
            for res in result:
                res.print()

        return list(result)


def check_platform() -> dict:
    """
    检查当前平台兼容性

    返回当前平台信息和各功能的兼容性状态。

    Returns:
        dict: 平台信息和兼容性状态

    Example:
        >>> from examples._common import check_platform
        >>> info = check_platform()
        >>> print(f"平台: {info['platform']}")
        >>> print(f"PaddleOCR-VL 支持: {info['supports_vl']}")
    """
    return {
        "platform": PLATFORM_INFO.get_platform_string(),
        "is_macos": PLATFORM_INFO.is_macos,
        "is_macos_arm": PLATFORM_INFO.is_macos_arm,
        "is_linux": PLATFORM_INFO.is_linux,
        "is_windows": PLATFORM_INFO.is_windows,
        "supports_vl": PLATFORM_INFO.supports_paddleocr_vl,
    }


# =============================================================================
# __all__ 定义
# __all__ Definition
# =============================================================================

__all__ = [
    # 版本
    "__version__",
    "__author__",
    # 异常
    "OCRException",
    "OCRInitError",
    "OCRProcessError",
    "OCRFileNotFoundError",
    "OCRConfigError",
    "OCROutputError",
    "OCRPlatformError",
    # 配置
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_ALIASES",
    "SUPPORTED_IMAGE_EXTENSIONS",
    "SUPPORTED_DOCUMENT_EXTENSIONS",
    "ALL_SUPPORTED_EXTENSIONS",
    "OCRDefaults",
    "StructureDefaults",
    "DEFAULT_OCR_CONFIG",
    "DEFAULT_STRUCTURE_CONFIG",
    "PathConfig",
    "PATH_CONFIG",
    "PlatformInfo",
    "PLATFORM_INFO",
    "OutputFormat",
    "is_supported_language",
    "normalize_language",
    "is_supported_image",
    "is_supported_document",
    "is_supported_input",
    # 日志
    "setup_logging",
    "get_logger",
    "LogContext",
    "ProgressLogger",
    "ColoredFormatter",
    # 基类
    "OCRContextManager",
    "StructureContextManager",
    "ocr_session",
    "structure_session",
    "BaseOCRProcessor",
    "OCRResultWrapper",
    "require_non_arm_mac",
    # 工具函数
    "ensure_directory",
    "validate_file_exists",
    "find_images",
    "get_output_path",
    "save_json",
    "load_json",
    "format_ocr_result",
    "extract_text_only",
    "join_texts",
    "clean_text",
    "get_timestamp",
    "get_file_stats",
    "format_file_size",
    "batch_process",
    "create_summary_report",
    "get_env_or_default",
    "set_paddleocr_env",
    "resize_image_for_ocr",
    # 便捷函数
    "quick_ocr",
    "check_platform",
]
