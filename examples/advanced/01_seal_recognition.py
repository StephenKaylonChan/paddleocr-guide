#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
印章识别示例 - 识别文档中的印章/公章
Seal/Stamp Recognition Example - Recognize Seals in Documents

本示例演示了如何使用 PP-StructureV3 识别文档中的印章（公章、私章等）。
印章识别功能可以检测印章区域并提取印章中的文字内容。

常见应用场景：
- 合同盖章检测
- 证书印章验证
- 公文印章识别
- 发票印章提取

This example demonstrates how to recognize seals/stamps in documents
using PP-StructureV3. Seal recognition can detect seal regions and
extract text content from seals.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/01_seal_recognition.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import gc
import sys
from dataclasses import dataclass, field
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
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class SealInfo:
    """
    单个印章的信息

    Attributes:
        index: 印章索引（从 0 开始）
        texts: 印章中的文字列表
        bbox: 边界框坐标 [x1, y1, x2, y2]
        confidence: 检测置信度
    """

    index: int
    texts: list[str] = field(default_factory=list)
    bbox: Optional[list[float]] = None
    confidence: float = 0.0

    @property
    def full_text(self) -> str:
        """拼接所有印章文字"""
        return "".join(self.texts)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "index": self.index,
            "texts": self.texts,
            "full_text": self.full_text,
            "bbox": self.bbox,
            "confidence": self.confidence,
        }


@dataclass
class SealRecognitionResult:
    """
    印章识别结果

    Attributes:
        source_file: 源文件路径
        seals: 识别到的印章列表
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    seals: list[SealInfo] = field(default_factory=list)
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def seal_count(self) -> int:
        """识别到的印章总数"""
        return len(self.seals)

    @property
    def all_texts(self) -> list[str]:
        """所有印章的文字列表"""
        texts = []
        for seal in self.seals:
            texts.extend(seal.texts)
        return texts

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "seal_count": self.seal_count,
            "page_count": self.page_count,
            "seals": [s.to_dict() for s in self.seals],
            "all_texts": self.all_texts,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 印章识别器类
# Seal Recognizer Class
# =============================================================================


class SealRecognizer:
    """
    印章识别器 - 识别文档中的印章

    该类封装了 PP-StructureV3 的印章识别功能，支持：
    - 检测文档中的所有印章区域
    - 提取印章中的文字内容
    - 支持红章、蓝章等各种颜色
    - 支持圆形章、椭圆章、方章等形状

    Attributes:
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> with SealRecognizer() as recognizer:
        ...     result = recognizer.recognize("contract.png")
        ...     for seal in result.seals:
        ...         print(f"印章文字: {seal.full_text}")
    """

    def __init__(
        self,
        *,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化印章识别器

        Args:
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "SealRecognizer":
        """初始化 PP-StructureV3 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化印章识别引擎...")

        try:
            from paddleocr import PPStructureV3

            # 仅启用印章识别，禁用其他功能以提高速度
            self._pipeline = PPStructureV3(
                use_seal_recognition=True,  # 启用印章识别
                use_table_recognition=False,  # 禁用表格识别
                use_formula_recognition=False,  # 禁用公式识别
                use_chart_recognition=False,  # 禁用图表识别
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
            )
            self._initialized = True
            logger.info("印章识别引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"印章识别引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "SealRecognizer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        save_visualization: bool = True,
    ) -> SealRecognitionResult:
        """
        识别图片中的印章

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            save_visualization: 是否保存可视化结果

        Returns:
            SealRecognitionResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("印章识别引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在识别印章: {path.name}")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            seals: list[SealInfo] = []
            page_count = 0
            seal_index = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 打印结果
                res.print()

                # 从 JSON 结果中提取印章信息
                try:
                    res_json = res.json
                    if "seal_res_list" in res_json:
                        for seal_data in res_json["seal_res_list"]:
                            seal_texts = seal_data.get("rec_texts", [])
                            seal_bbox = seal_data.get("bbox", None)

                            seal_info = SealInfo(
                                index=seal_index,
                                texts=seal_texts,
                                bbox=seal_bbox,
                            )
                            seals.append(seal_info)
                            seal_index += 1

                            logger.info(f"  发现印章 #{seal_index}: {seal_info.full_text}")
                except Exception as e:
                    logger.warning(f"解析印章结果时出错: {e}")

                # 保存结果
                if output_dir:
                    try:
                        res.save_to_json(save_path=str(output_path))

                        if save_visualization:
                            res.save_to_img(save_path=str(output_path))

                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"识别完成，共发现 {len(seals)} 个印章")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return SealRecognitionResult(
                source_file=str(path),
                seals=seals,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"印章识别失败: {e}")
            return SealRecognitionResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_seals(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> SealRecognitionResult:
    """
    便捷函数 - 识别图片中的印章

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        SealRecognitionResult: 识别结果

    Example:
        >>> result = recognize_seals("contract.png")
        >>> print(f"发现 {result.seal_count} 个印章")
        >>> for seal in result.seals:
        ...     print(f"  印章文字: {seal.full_text}")
    """
    with SealRecognizer() as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


def extract_seal_texts(image_path: Union[str, Path]) -> list[str]:
    """
    便捷函数 - 提取所有印章文字

    Args:
        image_path: 图片路径

    Returns:
        list[str]: 印章文字列表

    Example:
        >>> texts = extract_seal_texts("contract.png")
        >>> for text in texts:
        ...     print(text)
    """
    result = recognize_seals(image_path)
    return result.all_texts


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示印章识别功能

    该函数展示了 PP-StructureV3 的印章识别功能：
    1. 检测文档中的印章区域
    2. 提取印章中的文字
    3. 保存识别结果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-StructureV3 印章识别示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "seal"

    # 打印说明
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 包含印章/公章的文档图片")
    logger.info("  - 常见场景：合同、证书、公文")
    logger.info("")
    logger.info("支持的印章类型:")
    logger.info("  - 红色公章、蓝色私章")
    logger.info("  - 圆形章、椭圆章、方章")
    logger.info("  - 清晰和模糊印章")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备包含印章的文档图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用印章识别器
        with SealRecognizer() as recognizer:
            result = recognizer.recognize(
                image_path,
                output_dir=output_dir,
                save_visualization=True,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("识别完成!")
                logger.info(f"共处理 {result.page_count} 页")
                logger.info(f"发现 {result.seal_count} 个印章")

                if result.seals:
                    logger.info("")
                    logger.info("印章内容:")
                    for seal in result.seals:
                        logger.info(f"  印章 #{seal.index + 1}: {seal.full_text}")
            else:
                logger.error(f"识别失败: {result.error}")

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
