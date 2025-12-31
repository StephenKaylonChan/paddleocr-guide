#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义异常类 - OCR 处理相关异常
Custom Exceptions - OCR Processing Related Exceptions

本模块定义了 PaddleOCR 示例代码中使用的所有自定义异常类。
通过使用自定义异常，可以更精确地捕获和处理不同类型的错误，
提高代码的可读性和可维护性。

This module defines all custom exception classes used in PaddleOCR examples.
Using custom exceptions allows for more precise error handling and improves
code readability and maintainability.

作者: paddleocr-guide
API 版本: PaddleOCR 3.x
"""

from __future__ import annotations

from typing import Any, Optional


class OCRException(Exception):
    """
    OCR 异常基类 - 所有 OCR 相关异常的父类

    所有自定义 OCR 异常都应该继承此类，以便于统一捕获和处理。
    该类提供了标准的异常信息格式化和错误代码支持。

    Attributes:
        message: 异常信息描述
        error_code: 可选的错误代码，用于程序化处理
        details: 可选的额外详细信息字典

    Example:
        >>> try:
        ...     raise OCRException("处理失败", error_code="E001")
        ... except OCRException as e:
        ...     print(f"错误代码: {e.error_code}, 信息: {e.message}")
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        初始化 OCR 异常

        Args:
            message: 异常信息描述，应该清晰说明错误原因
            error_code: 可选的错误代码，格式建议为 "E001" 形式
            details: 可选的额外详细信息，如文件路径、参数值等
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化异常信息，包含错误代码（如果有）"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """返回异常的详细表示形式，便于调试"""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"details={self.details!r})"
        )


class OCRInitError(OCRException):
    """
    OCR 初始化错误 - 模型加载或引擎初始化失败时抛出

    当 PaddleOCR 引擎无法正常初始化时抛出此异常。
    常见原因包括：
    - 依赖库未安装（如 paddleocr, paddlepaddle）
    - 模型文件下载失败或损坏
    - 内存不足无法加载模型
    - GPU/CUDA 配置问题

    Example:
        >>> try:
        ...     ocr = PaddleOCR(lang='invalid_lang')
        ... except Exception as e:
        ...     raise OCRInitError(
        ...         "OCR 引擎初始化失败",
        ...         error_code="E101",
        ...         details={"lang": "invalid_lang", "original_error": str(e)}
        ...     )
    """

    def __init__(
        self,
        message: str = "OCR 引擎初始化失败",
        *,
        error_code: Optional[str] = "E101",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code=error_code, details=details)


class OCRProcessError(OCRException):
    """
    OCR 处理错误 - 图像识别或文档处理过程中出错时抛出

    当图像识别过程中发生错误时抛出此异常。
    常见原因包括：
    - 图像格式不支持或损坏
    - 图像尺寸过大或过小
    - 识别超时
    - 内部处理错误

    Attributes:
        image_path: 可选的图像路径，便于追踪问题文件

    Example:
        >>> try:
        ...     result = ocr.predict("corrupted.png")
        ... except Exception as e:
        ...     raise OCRProcessError(
        ...         "图像识别失败",
        ...         image_path="corrupted.png",
        ...         details={"original_error": str(e)}
        ...     )
    """

    def __init__(
        self,
        message: str = "OCR 处理失败",
        *,
        image_path: Optional[str] = None,
        error_code: Optional[str] = "E201",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.image_path = image_path
        details = details or {}
        if image_path:
            details["image_path"] = image_path
        super().__init__(message, error_code=error_code, details=details)


class OCRFileNotFoundError(OCRException):
    """
    OCR 文件未找到错误 - 输入文件不存在时抛出

    当指定的图像或文档文件不存在时抛出此异常。
    该异常继承自 OCRException 而非 Python 内置的 FileNotFoundError，
    以便于统一的 OCR 异常处理流程。

    Attributes:
        file_path: 不存在的文件路径

    Example:
        >>> from pathlib import Path
        >>> image_path = Path("nonexistent.png")
        >>> if not image_path.exists():
        ...     raise OCRFileNotFoundError(
        ...         f"图像文件不存在: {image_path}",
        ...         file_path=str(image_path)
        ...     )
    """

    def __init__(
        self,
        message: str = "文件不存在",
        *,
        file_path: Optional[str] = None,
        error_code: Optional[str] = "E301",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.file_path = file_path
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        super().__init__(message, error_code=error_code, details=details)


class OCRConfigError(OCRException):
    """
    OCR 配置错误 - 配置参数无效或缺失时抛出

    当 OCR 引擎配置参数无效时抛出此异常。
    常见原因包括：
    - 不支持的语言代码
    - 无效的参数组合
    - 必需参数缺失
    - 参数值超出有效范围

    Example:
        >>> lang = "unsupported_language"
        >>> if lang not in SUPPORTED_LANGUAGES:
        ...     raise OCRConfigError(
        ...         f"不支持的语言: {lang}",
        ...         details={"lang": lang, "supported": list(SUPPORTED_LANGUAGES.keys())}
        ...     )
    """

    def __init__(
        self,
        message: str = "配置参数无效",
        *,
        error_code: Optional[str] = "E401",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code=error_code, details=details)


class OCROutputError(OCRException):
    """
    OCR 输出错误 - 结果保存或导出失败时抛出

    当无法保存或导出 OCR 结果时抛出此异常。
    常见原因包括：
    - 输出目录不存在且无法创建
    - 没有写入权限
    - 磁盘空间不足
    - 文件被占用

    Attributes:
        output_path: 可选的输出路径

    Example:
        >>> try:
        ...     result.save_to_json("/readonly/path/output.json")
        ... except PermissionError as e:
        ...     raise OCROutputError(
        ...         "无法保存结果：权限不足",
        ...         output_path="/readonly/path/output.json"
        ...     )
    """

    def __init__(
        self,
        message: str = "结果保存失败",
        *,
        output_path: Optional[str] = None,
        error_code: Optional[str] = "E501",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.output_path = output_path
        details = details or {}
        if output_path:
            details["output_path"] = output_path
        super().__init__(message, error_code=error_code, details=details)


class OCRPlatformError(OCRException):
    """
    OCR 平台兼容性错误 - 当前平台不支持某功能时抛出

    当尝试在不支持的平台上使用某些功能时抛出此异常。
    例如：PaddleOCR-VL 不支持 macOS ARM (M1/M2/M3/M4) 芯片。

    Attributes:
        platform: 当前运行平台信息
        feature: 不支持的功能名称

    Example:
        >>> import platform
        >>> if platform.machine() == 'arm64' and platform.system() == 'Darwin':
        ...     raise OCRPlatformError(
        ...         "PaddleOCR-VL 不支持 macOS ARM 芯片",
        ...         platform="macOS ARM64",
        ...         feature="PaddleOCR-VL"
        ...     )
    """

    def __init__(
        self,
        message: str = "当前平台不支持此功能",
        *,
        platform_info: Optional[str] = None,
        feature: Optional[str] = None,
        error_code: Optional[str] = "E601",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.platform_info = platform_info
        self.feature = feature
        details = details or {}
        if platform_info:
            details["platform"] = platform_info
        if feature:
            details["feature"] = feature
        super().__init__(message, error_code=error_code, details=details)


# 异常错误代码参考表
# Error Code Reference Table
#
# E1xx - 初始化错误 (Initialization Errors)
#   E101 - OCR 引擎初始化失败
#   E102 - 模型加载失败
#   E103 - 依赖缺失
#
# E2xx - 处理错误 (Processing Errors)
#   E201 - 图像识别失败
#   E202 - 文档解析失败
#   E203 - 表格识别失败
#   E204 - 公式识别失败
#
# E3xx - 文件错误 (File Errors)
#   E301 - 文件不存在
#   E302 - 文件格式不支持
#   E303 - 文件损坏
#
# E4xx - 配置错误 (Configuration Errors)
#   E401 - 参数无效
#   E402 - 语言不支持
#   E403 - 参数冲突
#
# E5xx - 输出错误 (Output Errors)
#   E501 - 保存失败
#   E502 - 权限不足
#   E503 - 磁盘空间不足
#
# E6xx - 平台错误 (Platform Errors)
#   E601 - 平台不支持
#   E602 - GPU 不可用
#   E603 - 内存不足
