#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量 OCR 示例 - 处理多张图片
Batch OCR Example - Process Multiple Images

本示例演示了如何使用 PaddleOCR 批量处理目录中的所有图片。
通过使用类封装和上下文管理器，实现高效的批量识别。

This example demonstrates how to use PaddleOCR to batch process
all images in a directory. Efficient batch recognition is achieved
through class encapsulation and context managers.

适用模型: PP-OCRv5 (默认，~10MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/basic/02_batch_ocr.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import gc
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional, Union

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples._common import (  # 异常类; 日志; 配置; 工具函数
    PATH_CONFIG,
    SUPPORTED_IMAGE_EXTENSIONS,
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    OCROutputError,
    OCRProcessError,
    ProgressLogger,
    create_summary_report,
    ensure_directory,
    find_images,
    format_ocr_result,
    get_logger,
    get_timestamp,
    save_json,
    setup_logging,
    validate_file_exists,
)

# 配置模块日志器
logger = get_logger(__name__)


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class ImageResult:
    """
    单张图片的识别结果

    封装了单张图片的 OCR 识别结果，包括文件信息和识别的文本。

    Attributes:
        file_name: 文件名
        file_path: 完整文件路径
        text_count: 识别的文本行数
        texts: 识别的文本列表
        error: 如果处理失败，记录错误信息
        processing_time: 处理耗时（秒）
    """

    file_name: str
    file_path: str
    text_count: int = 0
    texts: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    processing_time: float = 0.0

    @property
    def is_success(self) -> bool:
        """是否处理成功"""
        return self.error is None

    @property
    def full_text(self) -> str:
        """拼接所有识别的文本"""
        return "\n".join(item.get("text", "") for item in self.texts)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "file": self.file_name,
            "path": self.file_path,
            "text_count": self.text_count,
            "texts": self.texts,
            "error": self.error,
            "processing_time": self.processing_time,
        }


@dataclass
class BatchResult:
    """
    批量处理的汇总结果

    Attributes:
        total: 总图片数
        success_count: 成功处理数
        failed_count: 失败数
        results: 所有图片的处理结果
        total_time: 总处理时间
        processed_at: 处理时间戳
    """

    total: int = 0
    success_count: int = 0
    failed_count: int = 0
    results: list[ImageResult] = field(default_factory=list)
    total_time: float = 0.0
    processed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.success_count / self.total if self.total > 0 else 0.0

    @property
    def total_text_count(self) -> int:
        """识别的总文本行数"""
        return sum(r.text_count for r in self.results if r.is_success)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "summary": {
                "total": self.total,
                "success": self.success_count,
                "failed": self.failed_count,
                "success_rate": f"{self.success_rate:.1%}",
                "total_text_count": self.total_text_count,
                "total_time": f"{self.total_time:.2f}s",
            },
            "processed_at": self.processed_at,
            "results": [r.to_dict() for r in self.results],
        }


# =============================================================================
# 批量 OCR 处理器类
# Batch OCR Processor Class
# =============================================================================


class BatchOCR:
    """
    批量 OCR 处理器

    该类封装了批量图片识别的完整流程，包括：
    - OCR 引擎初始化（仅初始化一次，提高效率）
    - 单张图片处理
    - 批量目录处理
    - 结果保存和汇总

    使用上下文管理器协议，确保资源正确释放。

    Attributes:
        lang: 语言代码
        ocr: PaddleOCR 实例
        _initialized: 是否已初始化

    Example:
        >>> # 使用上下文管理器（推荐）
        >>> with BatchOCR(lang='ch') as processor:
        ...     results = processor.process_directory("./images")
        ...     processor.save_summary(results, "./output")

        >>> # 手动管理（不推荐）
        >>> processor = BatchOCR()
        >>> try:
        ...     processor.initialize()
        ...     results = processor.process_directory("./images")
        ... finally:
        ...     processor.cleanup()
    """

    def __init__(
        self,
        lang: str = "ch",
        *,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
        use_textline_orientation: bool = False,
    ) -> None:
        """
        初始化批量处理器

        注意：初始化时不会立即加载模型，
        模型在 initialize() 或进入上下文时加载。

        Args:
            lang: 语言代码，默认 'ch'（中文）
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
            use_textline_orientation: 是否启用文本行方向分类
        """
        self.lang = lang
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping
        self.use_textline_orientation = use_textline_orientation

        self.ocr: Optional[Any] = None
        self._initialized: bool = False

        logger.debug(f"BatchOCR 配置: lang={lang}")

    def initialize(self) -> "BatchOCR":
        """
        初始化 OCR 引擎

        加载 PaddleOCR 模型。首次运行时会自动下载模型文件。

        Returns:
            BatchOCR: 返回自身，支持链式调用

        Raises:
            OCRInitError: 初始化失败时
        """
        if self._initialized:
            return self

        logger.info(f"正在初始化 OCR 引擎 (语言: {self.lang})...")

        try:
            from paddleocr import PaddleOCR

            self.ocr = PaddleOCR(
                lang=self.lang,
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
                use_textline_orientation=self.use_textline_orientation,
            )
            self._initialized = True
            logger.info("OCR 引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"OCR 引擎初始化失败: {e}",
                error_code="E101",
            ) from e

    def cleanup(self) -> None:
        """
        清理 OCR 资源

        释放 OCR 引擎占用的内存。多次调用是安全的。
        """
        if self.ocr is not None:
            logger.debug("正在清理 OCR 资源...")
            del self.ocr
            self.ocr = None
            self._initialized = False
            gc.collect()
            logger.debug("OCR 资源清理完成")

    def __enter__(self) -> "BatchOCR":
        """进入上下文，初始化 OCR 引擎"""
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """退出上下文，清理资源"""
        self.cleanup()
        return False

    def process_image(self, image_path: Union[str, Path]) -> ImageResult:
        """
        处理单张图片

        识别单张图片中的文字，返回结构化的结果对象。

        Args:
            image_path: 图片文件路径

        Returns:
            ImageResult: 识别结果对象

        Raises:
            OCRInitError: 如果 OCR 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("OCR 引擎未初始化，请先调用 initialize()")

        path = Path(image_path)
        start_time = datetime.now()

        try:
            # 执行识别
            result = self.ocr.predict(str(path))

            # 提取文本
            texts = format_ocr_result(result)

            processing_time = (datetime.now() - start_time).total_seconds()

            return ImageResult(
                file_name=path.name,
                file_path=str(path),
                text_count=len(texts),
                texts=texts,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.warning(f"处理失败: {path.name} - {e}")

            return ImageResult(
                file_name=path.name,
                file_path=str(path),
                error=str(e),
                processing_time=processing_time,
            )

    def process_directory(
        self,
        input_dir: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        recursive: bool = False,
        save_individual: bool = True,
    ) -> BatchResult:
        """
        批量处理目录中的所有图片

        扫描指定目录，处理所有支持格式的图片文件。

        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径（可选）
            recursive: 是否递归处理子目录
            save_individual: 是否保存每张图片的单独结果

        Returns:
            BatchResult: 批量处理结果汇总

        Raises:
            OCRFileNotFoundError: 目录不存在时
            OCRInitError: OCR 引擎未初始化时
        """
        if not self._initialized:
            raise OCRInitError("OCR 引擎未初始化")

        input_path = Path(input_dir)
        if not input_path.exists():
            raise OCRFileNotFoundError(
                f"目录不存在: {input_path}",
                file_path=str(input_path),
            )

        # 查找所有图片文件
        image_files = list(find_images(input_path, recursive=recursive))

        if not image_files:
            logger.warning(f"目录中没有找到图片文件: {input_path}")
            return BatchResult()

        logger.info(f"找到 {len(image_files)} 张图片，开始处理...")

        # 准备输出目录
        if output_dir:
            output_path = ensure_directory(output_dir)

        # 初始化结果
        batch_result = BatchResult(total=len(image_files))
        start_time = datetime.now()

        # 创建进度日志器
        progress = ProgressLogger(
            total=len(image_files),
            description="处理图片",
        )

        # 处理每张图片
        for i, img_path in enumerate(image_files, 1):
            progress.update(i, f"处理: {img_path.name}")

            result = self.process_image(img_path)
            batch_result.results.append(result)

            if result.is_success:
                batch_result.success_count += 1
                logger.debug(f"  检测到 {result.text_count} 行文字")

                # 保存单个文件的结果
                if output_dir and save_individual:
                    self._save_individual_result(result, output_path)
            else:
                batch_result.failed_count += 1
                logger.warning(f"  处理失败: {result.error}")

        batch_result.total_time = (datetime.now() - start_time).total_seconds()

        progress.finish()

        return batch_result

    def _save_individual_result(
        self,
        result: ImageResult,
        output_dir: Path,
    ) -> None:
        """保存单个图片的识别结果"""
        try:
            # 保存为文本文件
            txt_file = output_dir / f"{Path(result.file_name).stem}.txt"
            txt_file.write_text(result.full_text, encoding="utf-8")
        except Exception as e:
            logger.warning(f"保存结果失败: {result.file_name} - {e}")

    def save_summary(
        self,
        batch_result: BatchResult,
        output_dir: Union[str, Path],
    ) -> Path:
        """
        保存批量处理汇总结果

        将所有处理结果保存为 JSON 文件。

        Args:
            batch_result: 批量处理结果
            output_dir: 输出目录

        Returns:
            Path: 汇总文件路径
        """
        output_path = ensure_directory(output_dir)
        summary_file = output_path / f"summary_{get_timestamp()}.json"

        save_json(batch_result.to_dict(), summary_file)
        logger.info(f"汇总结果已保存: {summary_file}")

        return summary_file


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示批量 OCR 处理流程

    该函数展示了完整的批量 OCR 处理流程：
    1. 配置日志系统
    2. 创建批量处理器
    3. 处理测试目录中的所有图片
    4. 输出处理统计信息
    5. 保存汇总结果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 50)
    logger.info("PaddleOCR 批量 OCR 示例")
    logger.info("=" * 50)

    # 设置路径
    input_dir = PATH_CONFIG.test_images_dir
    output_dir = PATH_CONFIG.outputs_dir

    # 检查输入目录
    if not input_dir.exists():
        logger.warning(f"测试图片目录不存在: {input_dir}")
        logger.info("请将测试图片放入以下目录:")
        logger.info(f"  {input_dir}")
        return

    try:
        # 使用上下文管理器创建批量处理器
        with BatchOCR(lang="ch") as processor:
            # 处理目录中的所有图片
            results = processor.process_directory(
                input_dir,
                output_dir=output_dir,
                save_individual=True,
            )

            # 输出统计信息
            logger.info("")
            logger.info("=" * 50)
            logger.info("处理完成统计")
            logger.info("=" * 50)
            logger.info(f"  总图片数: {results.total}")
            logger.info(f"  成功处理: {results.success_count}")
            logger.info(f"  失败数量: {results.failed_count}")
            logger.info(f"  成功率: {results.success_rate:.1%}")
            logger.info(f"  总文字行数: {results.total_text_count}")
            logger.info(f"  总耗时: {results.total_time:.2f} 秒")

            # 保存汇总结果
            if results.total > 0:
                processor.save_summary(results, output_dir)

    except OCRFileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        raise SystemExit(1) from e

    except OCRInitError as e:
        logger.error(f"初始化错误: {e}")
        raise SystemExit(1) from e

    except OCRException as e:
        logger.error(f"OCR 错误: {e}")
        raise SystemExit(1) from e

    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
