#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档预处理示例 - 文档方向矫正与弯曲矫正
Document Preprocessing Example - Orientation and Unwarping Correction

本示例演示了如何使用 PP-StructureV3 对文档进行预处理，
包括方向检测与矫正、弯曲文档矫正等功能。

预处理功能：
- 文档方向检测与矫正（0°/90°/180°/270°）
- 弯曲文档矫正（处理翘起、卷曲的纸张）
- 透视变形修复

常见应用场景：
- 手机拍摄的文档照片
- 扫描仪倾斜扫描的文档
- 书籍弯曲的扫描页
- 证件照片的透视修复

This example demonstrates how to use PP-StructureV3 for document
preprocessing, including orientation detection/correction and
document unwarping.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/07_doc_preprocessing.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import gc
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples._common import (  # 异常类; 日志; 配置; 工具函数
    PATH_CONFIG,
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    ensure_directory,
    get_logger,
    setup_logging,
)

# 配置模块日志器
logger = get_logger(__name__)


# =============================================================================
# 预处理模式枚举
# Preprocessing Mode Enum
# =============================================================================


class PreprocessMode(Enum):
    """预处理模式"""

    FULL = "full"  # 完整预处理（方向 + 弯曲）
    ORIENTATION_ONLY = "orientation"  # 仅方向矫正
    UNWARPING_ONLY = "unwarping"  # 仅弯曲矫正
    NONE = "none"  # 不预处理（基准测试用）


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class PreprocessingResult:
    """
    文档预处理结果

    Attributes:
        source_file: 源文件路径
        mode: 预处理模式
        page_count: 页数
        orientation_corrected: 是否进行了方向矫正
        unwarping_applied: 是否进行了弯曲矫正
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    mode: str = PreprocessMode.FULL.value
    page_count: int = 0
    orientation_corrected: bool = False
    unwarping_applied: bool = False
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "mode": self.mode,
            "page_count": self.page_count,
            "orientation_corrected": self.orientation_corrected,
            "unwarping_applied": self.unwarping_applied,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 文档预处理器类
# Document Preprocessor Class
# =============================================================================


class DocumentPreprocessor:
    """
    文档预处理器 - 文档方向矫正与弯曲矫正

    该类封装了 PP-StructureV3 的预处理功能，支持：
    - 文档方向检测与矫正（自动检测 0°/90°/180°/270° 并矫正）
    - 弯曲文档矫正（处理翘起、卷曲、透视变形）
    - 可选择单独使用或组合使用

    预处理模式：
    - FULL: 完整预处理（方向 + 弯曲）
    - ORIENTATION_ONLY: 仅方向矫正
    - UNWARPING_ONLY: 仅弯曲矫正

    Attributes:
        mode: 预处理模式

    Example:
        >>> with DocumentPreprocessor(mode=PreprocessMode.FULL) as preprocessor:
        ...     result = preprocessor.process("tilted_photo.png")
        ...     print(f"方向矫正: {result.orientation_corrected}")
        ...     print(f"弯曲矫正: {result.unwarping_applied}")
    """

    def __init__(
        self,
        *,
        mode: PreprocessMode = PreprocessMode.FULL,
    ) -> None:
        """
        初始化文档预处理器

        Args:
            mode: 预处理模式
        """
        self.mode = mode

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "DocumentPreprocessor":
        """初始化 PP-StructureV3 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化文档预处理引擎...")
        logger.info(f"预处理模式: {self.mode.value}")

        try:
            from paddleocr import PPStructureV3

            # 根据模式配置参数
            use_orientation = self.mode in (PreprocessMode.FULL, PreprocessMode.ORIENTATION_ONLY)
            use_unwarping = self.mode in (PreprocessMode.FULL, PreprocessMode.UNWARPING_ONLY)

            self._pipeline = PPStructureV3(
                use_doc_orientation_classify=use_orientation,
                use_doc_unwarping=use_unwarping,
                use_table_recognition=True,  # 启用表格识别以验证效果
                use_formula_recognition=False,
                use_seal_recognition=False,
                use_chart_recognition=False,
            )
            self._initialized = True

            logger.info(f"  方向检测: {'启用' if use_orientation else '禁用'}")
            logger.info(f"  弯曲矫正: {'启用' if use_unwarping else '禁用'}")
            logger.info("文档预处理引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"文档预处理引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "DocumentPreprocessor":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def process(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        save_corrected_image: bool = True,
    ) -> PreprocessingResult:
        """
        预处理文档

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            save_corrected_image: 是否保存矫正后的图片

        Returns:
            PreprocessingResult: 预处理结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("文档预处理引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在预处理文档: {path.name}")

        # 确定预处理类型
        use_orientation = self.mode in (PreprocessMode.FULL, PreprocessMode.ORIENTATION_ONLY)
        use_unwarping = self.mode in (PreprocessMode.FULL, PreprocessMode.UNWARPING_ONLY)

        if use_orientation:
            logger.info("  步骤 1: 文档方向检测与矫正")
        if use_unwarping:
            step_num = 2 if use_orientation else 1
            logger.info(f"  步骤 {step_num}: 弯曲文档矫正")
        logger.info("  后续: OCR 识别")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            page_count = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 打印结果
                res.print()

                # 保存结果
                if output_dir:
                    try:
                        # 保存预处理后的图片
                        if save_corrected_image:
                            res.save_to_img(save_path=str(output_path))

                        res.save_to_json(save_path=str(output_path))
                        res.save_to_markdown(save_path=str(output_path))
                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"预处理完成，共处理 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")
                if save_corrected_image:
                    logger.info("包含预处理后的图片")

            return PreprocessingResult(
                source_file=str(path),
                mode=self.mode.value,
                page_count=page_count,
                orientation_corrected=use_orientation,
                unwarping_applied=use_unwarping,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"文档预处理失败: {e}")
            return PreprocessingResult(
                source_file=str(path),
                mode=self.mode.value,
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def preprocess_document(
    image_path: Union[str, Path],
    *,
    mode: PreprocessMode = PreprocessMode.FULL,
    output_dir: Optional[Union[str, Path]] = None,
) -> PreprocessingResult:
    """
    便捷函数 - 预处理文档

    Args:
        image_path: 图片路径
        mode: 预处理模式
        output_dir: 输出目录（可选）

    Returns:
        PreprocessingResult: 预处理结果

    Example:
        >>> result = preprocess_document("tilted_photo.png")
        >>> print(f"处理完成: {result.success}")
    """
    with DocumentPreprocessor(mode=mode) as preprocessor:
        return preprocessor.process(image_path, output_dir=output_dir)


def correct_orientation(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> PreprocessingResult:
    """
    便捷函数 - 仅进行方向矫正

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        PreprocessingResult: 预处理结果
    """
    return preprocess_document(
        image_path,
        mode=PreprocessMode.ORIENTATION_ONLY,
        output_dir=output_dir,
    )


def unwarp_document(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> PreprocessingResult:
    """
    便捷函数 - 仅进行弯曲矫正

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        PreprocessingResult: 预处理结果
    """
    return preprocess_document(
        image_path,
        mode=PreprocessMode.UNWARPING_ONLY,
        output_dir=output_dir,
    )


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示文档预处理功能

    该函数展示了 PP-StructureV3 的预处理功能：
    1. 文档方向检测与矫正
    2. 弯曲文档矫正
    3. 不同模式的使用方法
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-StructureV3 文档预处理示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "preprocessing"

    # 打印说明
    logger.info("")
    logger.info("预处理功能:")
    logger.info("  1. use_doc_orientation_classify  # 文档方向检测与矫正")
    logger.info("     - 检测文档是否旋转（0°/90°/180°/270°）")
    logger.info("     - 自动矫正到正确方向")
    logger.info("")
    logger.info("  2. use_doc_unwarping             # 弯曲文档矫正")
    logger.info("     - 矫正弯曲、卷曲的文档")
    logger.info("     - 修复透视变形")
    logger.info("")
    logger.info("预处理模式:")
    logger.info("  - FULL: 完整预处理（方向 + 弯曲）")
    logger.info("  - ORIENTATION_ONLY: 仅方向矫正")
    logger.info("  - UNWARPING_ONLY: 仅弯曲矫正")
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 倾斜拍摄的文档")
    logger.info("  - 弯曲或卷曲的纸张")
    logger.info("  - 手机拍摄的文档")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备需要预处理的文档图片")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 完整预处理模式
        logger.info("【完整预处理模式】")
        with DocumentPreprocessor(mode=PreprocessMode.FULL) as preprocessor:
            result = preprocessor.process(
                image_path,
                output_dir=output_dir,
                save_corrected_image=True,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("预处理完成!")
                logger.info(f"共处理 {result.page_count} 页")
                logger.info(f"方向矫正: {'已执行' if result.orientation_corrected else '未执行'}")
                logger.info(f"弯曲矫正: {'已执行' if result.unwarping_applied else '未执行'}")
            else:
                logger.error(f"预处理失败: {result.error}")

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
