#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础类 - OCR 上下文管理器和基础抽象类
Base Classes - OCR Context Managers and Base Abstract Classes

本模块提供了 OCR 处理的核心基础设施，包括：
- OCRContextManager: 上下文管理器，自动处理资源初始化和清理
- BaseOCRProcessor: 抽象基类，定义 OCR 处理器的标准接口
- ResultWrapper: 结果包装类，统一结果处理方式

通过使用这些基础类，可以确保：
1. 资源正确初始化和释放
2. 异常统一处理
3. 代码结构一致性

This module provides core infrastructure for OCR processing, including:
- OCRContextManager: Context manager for automatic resource management
- BaseOCRProcessor: Abstract base class defining standard OCR processor interface
- ResultWrapper: Result wrapper class for unified result handling

作者: paddleocr-guide
API 版本: PaddleOCR 3.x
"""

from __future__ import annotations

import gc
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Generic,
    Iterator,
    Optional,
    TypeVar,
    Union,
)

from .config import DEFAULT_OCR_CONFIG, PLATFORM_INFO, is_supported_input
from .exceptions import (
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    OCRPlatformError,
    OCRProcessError,
)
from .logging_config import get_logger

if TYPE_CHECKING:
    from paddleocr import PaddleOCR, PPStructureV3

# 类型变量
T = TypeVar("T")
OCRResult = TypeVar("OCRResult")

# 模块日志器
logger = get_logger(__name__)


# =============================================================================
# OCR 上下文管理器
# OCR Context Manager
# =============================================================================


class OCRContextManager:
    """
    OCR 上下文管理器 - 自动管理 OCR 引擎生命周期

    该类实现了 Python 上下文管理器协议，用于：
    1. 自动初始化 OCR 引擎
    2. 在使用完毕后自动清理资源
    3. 统一异常处理

    使用上下文管理器可以确保即使发生异常，资源也能正确释放。

    Attributes:
        lang: 语言代码
        ocr: PaddleOCR 实例（在 __enter__ 中创建）
        _initialized: 是否已初始化

    Example:
        >>> with OCRContextManager(lang='ch') as ocr:
        ...     result = ocr.predict('image.png')
        ...     for res in result:
        ...         res.print()
        # 退出 with 块时自动清理资源

        >>> # 也可以手动使用
        >>> manager = OCRContextManager()
        >>> try:
        ...     ocr = manager.initialize()
        ...     result = ocr.predict('image.png')
        ... finally:
        ...     manager.cleanup()
    """

    def __init__(
        self,
        lang: str = "ch",
        *,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
        use_textline_orientation: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        初始化上下文管理器

        Args:
            lang: 语言代码，默认 'ch'（中文）
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
            use_textline_orientation: 是否启用文本行方向分类
            **kwargs: 其他传递给 PaddleOCR 的参数
        """
        self.lang = lang
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping
        self.use_textline_orientation = use_textline_orientation
        self.extra_kwargs = kwargs

        self.ocr: Optional[PaddleOCR] = None
        self._initialized: bool = False

    def initialize(self) -> "PaddleOCR":
        """
        初始化 OCR 引擎

        Returns:
            PaddleOCR: 初始化后的 OCR 实例

        Raises:
            OCRInitError: 初始化失败时抛出
        """
        if self._initialized and self.ocr is not None:
            return self.ocr

        logger.info(f"正在初始化 OCR 引擎 (语言: {self.lang})...")

        try:
            from paddleocr import PaddleOCR

            self.ocr = PaddleOCR(
                lang=self.lang,
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
                use_textline_orientation=self.use_textline_orientation,
                **self.extra_kwargs,
            )
            self._initialized = True
            logger.info("OCR 引擎初始化完成")
            return self.ocr

        except ImportError as e:
            logger.error("PaddleOCR 未安装")
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
                details={"original_error": str(e)},
            ) from e

        except Exception as e:
            logger.error(f"OCR 引擎初始化失败: {e}")
            raise OCRInitError(
                f"OCR 引擎初始化失败: {e}",
                error_code="E101",
                details={"lang": self.lang, "original_error": str(e)},
            ) from e

    def cleanup(self) -> None:
        """
        清理 OCR 资源

        释放 OCR 引擎占用的内存和其他资源。
        即使多次调用也是安全的。
        """
        if self.ocr is not None:
            logger.debug("正在清理 OCR 资源...")
            try:
                # 删除 OCR 实例
                del self.ocr
                self.ocr = None
                self._initialized = False

                # 强制垃圾回收
                gc.collect()

                logger.debug("OCR 资源清理完成")
            except Exception as e:
                logger.warning(f"OCR 资源清理时出现警告: {e}")

    def __enter__(self) -> "PaddleOCR":
        """进入上下文，初始化并返回 OCR 实例"""
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        退出上下文，清理资源

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息

        Returns:
            bool: 是否抑制异常（始终返回 False，不抑制异常）
        """
        self.cleanup()

        # 如果有异常，记录日志
        if exc_type is not None:
            if issubclass(exc_type, OCRException):
                logger.error(f"OCR 处理异常: {exc_val}")
            else:
                logger.exception(f"未预期的异常: {exc_val}")

        # 不抑制异常
        return False


# =============================================================================
# 结构分析上下文管理器
# Structure Analysis Context Manager
# =============================================================================


class StructureContextManager:
    """
    PP-StructureV3 上下文管理器

    用于管理文档结构分析引擎的生命周期，与 OCRContextManager 类似。

    Example:
        >>> with StructureContextManager(use_table_recognition=True) as structure:
        ...     result = structure.predict('document.pdf')
    """

    def __init__(
        self,
        *,
        use_table_recognition: bool = True,
        use_seal_recognition: bool = False,
        use_formula_recognition: bool = False,
        use_chart_recognition: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        初始化结构分析上下文管理器

        Args:
            use_table_recognition: 是否启用表格识别
            use_seal_recognition: 是否启用印章识别
            use_formula_recognition: 是否启用公式识别
            use_chart_recognition: 是否启用图表识别
            **kwargs: 其他传递给 PPStructureV3 的参数
        """
        self.use_table_recognition = use_table_recognition
        self.use_seal_recognition = use_seal_recognition
        self.use_formula_recognition = use_formula_recognition
        self.use_chart_recognition = use_chart_recognition
        self.extra_kwargs = kwargs

        self.structure: Optional[PPStructureV3] = None
        self._initialized: bool = False

    def initialize(self) -> "PPStructureV3":
        """初始化结构分析引擎"""
        if self._initialized and self.structure is not None:
            return self.structure

        logger.info("正在初始化 PP-StructureV3...")

        try:
            from paddleocr import PPStructureV3

            self.structure = PPStructureV3(
                use_table_recognition=self.use_table_recognition,
                use_seal_recognition=self.use_seal_recognition,
                use_formula_recognition=self.use_formula_recognition,
                use_chart_recognition=self.use_chart_recognition,
                **self.extra_kwargs,
            )
            self._initialized = True
            logger.info("PP-StructureV3 初始化完成")
            return self.structure

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装",
                error_code="E103",
                details={"original_error": str(e)},
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"PP-StructureV3 初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理结构分析资源"""
        if self.structure is not None:
            del self.structure
            self.structure = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "PPStructureV3":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False


# =============================================================================
# 抽象基类
# Abstract Base Classes
# =============================================================================


class BaseOCRProcessor(ABC, Generic[T]):
    """
    OCR 处理器抽象基类

    定义了 OCR 处理器的标准接口，所有具体的处理器都应该继承此类。
    使用泛型 T 表示处理结果的类型。

    Subclasses must implement:
        - process(): 核心处理方法
        - cleanup(): 资源清理方法

    Example:
        >>> class ImageOCRProcessor(BaseOCRProcessor[dict]):
        ...     def process(self, input_path: Path) -> dict:
        ...         # 实现具体处理逻辑
        ...         pass
        ...
        ...     def cleanup(self) -> None:
        ...         # 实现资源清理
        ...         pass
    """

    def __init__(self, lang: str = "ch", **kwargs: Any) -> None:
        """
        初始化处理器

        Args:
            lang: 语言代码
            **kwargs: 其他配置参数
        """
        self.lang = lang
        self.config = kwargs
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def process(self, input_path: Union[str, Path]) -> T:
        """
        处理输入文件

        Args:
            input_path: 输入文件路径

        Returns:
            T: 处理结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRProcessError: 处理失败
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """清理处理器资源"""
        pass

    def validate_input(self, input_path: Union[str, Path]) -> Path:
        """
        验证输入文件

        Args:
            input_path: 输入文件路径

        Returns:
            Path: 验证后的路径对象

        Raises:
            OCRFileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
        """
        path = Path(input_path)

        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        if not is_supported_input(path):
            raise ValueError(f"不支持的文件格式: {path.suffix}")

        return path

    def __enter__(self) -> "BaseOCRProcessor[T]":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False


# =============================================================================
# 结果包装类
# Result Wrapper Classes
# =============================================================================


@dataclass
class OCRResultWrapper:
    """
    OCR 结果包装类

    统一包装 OCR 识别结果，提供便捷的访问和保存方法。

    Attributes:
        file_path: 源文件路径
        texts: 识别的文本列表
        raw_result: 原始结果对象
        metadata: 额外元数据

    Example:
        >>> result = OCRResultWrapper(
        ...     file_path="image.png",
        ...     texts=[{"text": "Hello", "confidence": 0.99}],
        ... )
        >>> print(result.full_text)
        'Hello'
        >>> result.save_to_txt("output.txt")
    """

    file_path: str
    texts: list[dict[str, Any]] = field(default_factory=list)
    raw_result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text_count(self) -> int:
        """识别的文本行数"""
        return len(self.texts)

    @property
    def full_text(self) -> str:
        """拼接所有识别的文本"""
        return "\n".join(item.get("text", "") for item in self.texts)

    @property
    def average_confidence(self) -> float:
        """平均置信度"""
        if not self.texts:
            return 0.0
        confidences = [item.get("confidence", 0.0) for item in self.texts if "confidence" in item]
        return sum(confidences) / len(confidences) if confidences else 0.0

    def save_to_txt(self, output_path: Union[str, Path]) -> None:
        """保存为纯文本文件"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.full_text, encoding="utf-8")
        logger.info(f"文本已保存: {path}")

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "text_count": self.text_count,
            "texts": self.texts,
            "average_confidence": self.average_confidence,
            "metadata": self.metadata,
        }


# =============================================================================
# 便捷上下文管理器
# Convenience Context Managers
# =============================================================================


@contextmanager
def ocr_session(
    lang: str = "ch",
    **kwargs: Any,
) -> Generator["PaddleOCR", None, None]:
    """
    便捷的 OCR 会话上下文管理器

    这是 OCRContextManager 的函数式替代方案。

    Args:
        lang: 语言代码
        **kwargs: 其他 PaddleOCR 参数

    Yields:
        PaddleOCR: OCR 实例

    Example:
        >>> with ocr_session(lang='ch') as ocr:
        ...     result = ocr.predict('image.png')
    """
    manager = OCRContextManager(lang=lang, **kwargs)
    try:
        yield manager.initialize()
    finally:
        manager.cleanup()


@contextmanager
def structure_session(**kwargs: Any) -> Generator["PPStructureV3", None, None]:
    """
    便捷的结构分析会话上下文管理器

    Args:
        **kwargs: PPStructureV3 参数

    Yields:
        PPStructureV3: 结构分析实例
    """
    manager = StructureContextManager(**kwargs)
    try:
        yield manager.initialize()
    finally:
        manager.cleanup()


# =============================================================================
# 平台检查装饰器
# Platform Check Decorators
# =============================================================================


def require_non_arm_mac(func: Callable[..., T]) -> Callable[..., T]:
    """
    装饰器：要求非 macOS ARM 平台

    用于标记不支持 macOS ARM 的功能（如 PaddleOCR-VL）。

    Example:
        >>> @require_non_arm_mac
        ... def use_paddleocr_vl(image_path: str):
        ...     from paddleocr import PaddleOCRVL
        ...     vl = PaddleOCRVL()
        ...     return vl.predict(image_path)
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        if PLATFORM_INFO.is_macos_arm:
            raise OCRPlatformError(
                "此功能不支持 macOS ARM (M1/M2/M3/M4) 芯片",
                platform_info=PLATFORM_INFO.get_platform_string(),
                feature=func.__name__,
            )
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
