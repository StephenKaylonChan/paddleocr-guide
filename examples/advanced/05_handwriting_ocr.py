#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写文字识别示例 - 识别手写文本
Handwriting Recognition Example - Recognize Handwritten Text

本示例演示了如何使用 PaddleOCR (PP-OCRv5) 识别手写文字。
通过调整检测和识别阈值，可以更好地处理潦草或倾斜的手写内容。

常见应用场景：
- 手写笔记数字化
- 手写表单识别
- 签名识别
- 批注提取

This example demonstrates how to recognize handwritten text
using PaddleOCR (PP-OCRv5). By adjusting detection and recognition
thresholds, it can better handle cursive or tilted handwriting.

适用模型: PP-OCRv5 (~10MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/05_handwriting_ocr.py

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
    format_ocr_result,
    get_logger,
    setup_logging,
)

# 配置模块日志器
logger = get_logger(__name__)


# =============================================================================
# 手写识别配置预设
# Handwriting Recognition Presets
# =============================================================================


@dataclass
class HandwritingConfig:
    """
    手写识别配置

    针对手写文字的特点，提供不同的配置预设。
    手写文字通常比印刷体更潦草、倾斜，需要降低阈值。

    Attributes:
        text_det_thresh: 文本检测置信度阈值
        text_det_box_thresh: 文本框阈值
        text_rec_score_thresh: 文本识别置信度阈值
        use_textline_orientation: 是否启用文本行方向检测
        use_doc_orientation_classify: 是否启用文档方向分类
    """

    text_det_thresh: float = 0.3
    text_det_box_thresh: float = 0.5
    text_rec_score_thresh: float = 0.3
    use_textline_orientation: bool = False  # macOS 内存优化：禁用文本行方向检测
    use_doc_orientation_classify: bool = False  # macOS 内存优化：禁用文档方向分类

    # 预设配置
    @classmethod
    def default(cls) -> "HandwritingConfig":
        """默认配置 - 平衡模式"""
        return cls()

    @classmethod
    def sensitive(cls) -> "HandwritingConfig":
        """高灵敏度配置 - 检测更多笔迹，但可能有噪音"""
        return cls(
            text_det_thresh=0.2,
            text_det_box_thresh=0.3,
            text_rec_score_thresh=0.2,
        )

    @classmethod
    def strict(cls) -> "HandwritingConfig":
        """严格配置 - 只保留高置信度结果"""
        return cls(
            text_det_thresh=0.5,
            text_det_box_thresh=0.6,
            text_rec_score_thresh=0.5,
        )


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class HandwritingText:
    """
    单条手写文本

    Attributes:
        text: 识别的文本内容
        confidence: 识别置信度
        bbox: 边界框坐标
    """

    text: str
    confidence: float = 0.0
    bbox: Optional[list[float]] = None

    @property
    def is_high_confidence(self) -> bool:
        """是否为高置信度（>= 50%）"""
        return self.confidence >= 0.5

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "is_high_confidence": self.is_high_confidence,
            "bbox": self.bbox,
        }


@dataclass
class HandwritingResult:
    """
    手写识别结果

    Attributes:
        source_file: 源文件路径
        texts: 识别到的文本列表
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    texts: list[HandwritingText] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    @property
    def text_count(self) -> int:
        """识别到的文本总数"""
        return len(self.texts)

    @property
    def high_confidence_count(self) -> int:
        """高置信度文本数量"""
        return sum(1 for t in self.texts if t.is_high_confidence)

    @property
    def average_confidence(self) -> float:
        """平均置信度"""
        if not self.texts:
            return 0.0
        return sum(t.confidence for t in self.texts) / len(self.texts)

    @property
    def full_text(self) -> str:
        """拼接所有文本"""
        return "\n".join(t.text for t in self.texts)

    def filter_by_confidence(self, min_confidence: float = 0.5) -> list[HandwritingText]:
        """按置信度过滤"""
        return [t for t in self.texts if t.confidence >= min_confidence]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "text_count": self.text_count,
            "high_confidence_count": self.high_confidence_count,
            "average_confidence": self.average_confidence,
            "texts": [t.to_dict() for t in self.texts],
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 手写识别器类
# Handwriting Recognizer Class
# =============================================================================


class HandwritingRecognizer:
    """
    手写文字识别器 - 识别手写文本

    该类封装了 PaddleOCR 的手写识别功能，通过优化的参数设置
    来更好地处理手写内容。

    优化策略：
    - 降低检测阈值：捕获更多潦草笔迹
    - 启用方向检测：处理倾斜文字
    - 按置信度过滤：去除噪音结果

    Attributes:
        config: 手写识别配置
        lang: 语言代码

    Example:
        >>> with HandwritingRecognizer() as recognizer:
        ...     result = recognizer.recognize("handwritten_note.png")
        ...     print(f"识别到 {result.text_count} 行文字")
        ...     for text in result.filter_by_confidence(0.5):
        ...         print(f"  {text.text} ({text.confidence:.1%})")
    """

    def __init__(
        self,
        *,
        config: Optional[HandwritingConfig] = None,
        lang: str = "ch",
    ) -> None:
        """
        初始化手写识别器

        Args:
            config: 手写识别配置，默认使用平衡模式
            lang: 语言代码，默认 'ch'（支持中英文混合）
        """
        self.config = config or HandwritingConfig.default()
        self.lang = lang

        self._ocr: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "HandwritingRecognizer":
        """初始化 OCR 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化手写识别引擎...")
        logger.info(f"语言: {self.lang}")
        logger.info(f"检测阈值: {self.config.text_det_thresh}")
        logger.info(f"识别阈值: {self.config.text_rec_score_thresh}")

        try:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                lang=self.lang,
                use_textline_orientation=self.config.use_textline_orientation,
                use_doc_orientation_classify=self.config.use_doc_orientation_classify,
                use_doc_unwarping=False,  # macOS 内存优化：禁用文档弯曲矫正
                text_det_thresh=self.config.text_det_thresh,
                text_det_box_thresh=self.config.text_det_box_thresh,
                text_rec_score_thresh=self.config.text_rec_score_thresh,
            )
            self._initialized = True
            logger.info("手写识别引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"手写识别引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._ocr is not None:
            del self._ocr
            self._ocr = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "HandwritingRecognizer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        min_confidence: float = 0.0,
    ) -> HandwritingResult:
        """
        识别手写文字

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            min_confidence: 最低置信度阈值（默认 0，返回所有结果）

        Returns:
            HandwritingResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("手写识别引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在识别手写文字: {path.name}")

        try:
            # 执行预测
            result = self._ocr.predict(str(path))

            texts: list[HandwritingText] = []

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in result:
                # 打印结果
                res.print()

                # 提取文本
                try:
                    res_json = res.json
                    rec_texts = res_json.get("rec_texts", [])
                    rec_scores = res_json.get("rec_scores", [])
                    dt_polys = res_json.get("dt_polys", [])

                    for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                        if score >= min_confidence:
                            bbox = dt_polys[i] if i < len(dt_polys) else None
                            handwriting_text = HandwritingText(
                                text=text,
                                confidence=score,
                                bbox=bbox,
                            )
                            texts.append(handwriting_text)
                except Exception as e:
                    logger.warning(f"解析结果时出错: {e}")

                # 保存结果
                if output_dir:
                    try:
                        res.save_to_json(save_path=str(output_path))
                        res.save_to_img(save_path=str(output_path))
                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"识别完成，共 {len(texts)} 行文字")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return HandwritingResult(
                source_file=str(path),
                texts=texts,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"手写识别失败: {e}")
            return HandwritingResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_handwriting(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[HandwritingConfig] = None,
) -> HandwritingResult:
    """
    便捷函数 - 识别手写文字

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）
        config: 手写识别配置（可选）

    Returns:
        HandwritingResult: 识别结果

    Example:
        >>> result = recognize_handwriting("note.png")
        >>> print(f"识别到 {result.text_count} 行")
        >>> print(result.full_text)
    """
    with HandwritingRecognizer(config=config) as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


def recognize_handwriting_sensitive(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> HandwritingResult:
    """
    便捷函数 - 高灵敏度手写识别

    使用较低的阈值，可以识别更多潦草的笔迹，
    但可能会产生一些噪音结果。

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        HandwritingResult: 识别结果
    """
    return recognize_handwriting(
        image_path,
        output_dir=output_dir,
        config=HandwritingConfig.sensitive(),
    )


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示手写文字识别功能

    该函数展示了 PaddleOCR 的手写识别功能：
    1. 使用优化参数识别手写文字
    2. 按置信度过滤结果
    3. 展示不同配置的效果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-OCRv5 手写文字识别示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "handwriting"

    # 打印说明
    logger.info("")
    logger.info("优化参数说明:")
    logger.info("  - use_textline_orientation=True  # 处理倾斜文字")
    logger.info("  - text_det_thresh=0.3            # 降低检测阈值")
    logger.info("  - text_rec_score_thresh=0.3      # 降低识别阈值")
    logger.info("")
    logger.info("配置预设:")
    logger.info("  - default()    # 平衡模式")
    logger.info("  - sensitive()  # 高灵敏度（检测更多笔迹）")
    logger.info("  - strict()     # 严格模式（只保留高置信度）")
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 手写笔记、便签、批注")
    logger.info("  - 尽量清晰，对比度高")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备手写文档图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用手写识别器
        with HandwritingRecognizer() as recognizer:
            result = recognizer.recognize(
                image_path,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("识别完成!")
                logger.info(f"总文本行数: {result.text_count}")
                logger.info(f"高置信度行数: {result.high_confidence_count}")
                logger.info(f"平均置信度: {result.average_confidence:.1%}")

                # 显示高置信度结果
                high_conf_texts = result.filter_by_confidence(0.5)
                if high_conf_texts:
                    logger.info("")
                    logger.info("高置信度结果 (>= 50%):")
                    for text in high_conf_texts[:10]:
                        logger.info(f"  {text.text} ({text.confidence:.1%})")
                    if len(high_conf_texts) > 10:
                        logger.info(f"  ... 共 {len(high_conf_texts)} 条")

                # 显示所有结果
                if result.texts:
                    logger.info("")
                    logger.info("所有识别结果:")
                    for i, text in enumerate(result.texts[:15], 1):
                        status = "✓" if text.is_high_confidence else "○"
                        logger.info(f"  {status} [{i}] {text.text} ({text.confidence:.1%})")
                    if result.text_count > 15:
                        logger.info(f"  ... 共 {result.text_count} 条")
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
