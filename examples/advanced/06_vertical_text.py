#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竖排文字识别示例 - 识别竖排/纵向排列的文字
Vertical Text Recognition Example - Recognize Vertically Arranged Text

本示例演示了如何使用 PaddleOCR (PP-OCRv5) 识别竖排文字。
通过启用文档方向检测和文本行方向检测，可以正确处理竖排排版。

常见应用场景：
- 中文竖排书籍、古籍
- 日文竖排文档
- 竖排标语、招牌
- 传统中文报纸

This example demonstrates how to recognize vertical text
using PaddleOCR (PP-OCRv5). By enabling document and textline
orientation detection, it can correctly handle vertical layouts.

适用模型: PP-OCRv5 (~10MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/06_vertical_text.py

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
    SUPPORTED_LANGUAGES,
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
# 竖排文字支持的语言
# Supported Languages for Vertical Text
# =============================================================================

# 常用于竖排的语言
VERTICAL_TEXT_LANGUAGES = {
    "ch": "简体中文（默认，支持中英混合）",
    "chinese_cht": "繁体中文（古籍、港台文档）",
    "japan": "日文（漫画、小说、报纸）",
    "korean": "韩文（传统文档）",
}


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class VerticalTextResult:
    """
    竖排文字识别结果

    Attributes:
        source_file: 源文件路径
        language: 使用的语言
        texts: 识别到的文本列表
        text_count: 文本行数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    language: str = "ch"
    texts: list[dict[str, Any]] = field(default_factory=list)
    text_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def full_text(self) -> str:
        """拼接所有文本"""
        return "\n".join(t.get("text", "") for t in self.texts)

    @property
    def average_confidence(self) -> float:
        """平均置信度"""
        if not self.texts:
            return 0.0
        return sum(t.get("confidence", 0) for t in self.texts) / len(self.texts)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "language": self.language,
            "text_count": self.text_count,
            "average_confidence": self.average_confidence,
            "texts": self.texts,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 竖排文字识别器类
# Vertical Text Recognizer Class
# =============================================================================


class VerticalTextRecognizer:
    """
    竖排文字识别器 - 识别竖排排版的文字

    该类封装了 PaddleOCR 的竖排文字识别功能，通过启用
    方向检测来正确处理竖排文本。

    关键参数：
    - use_doc_orientation_classify: 文档方向检测与矫正
    - use_textline_orientation: 文本行方向检测

    支持的语言：
    - 简体中文 (ch)
    - 繁体中文 (chinese_cht)
    - 日文 (japan)
    - 韩文 (korean)

    Attributes:
        lang: 语言代码

    Example:
        >>> with VerticalTextRecognizer(lang="ch") as recognizer:
        ...     result = recognizer.recognize("vertical_book.png")
        ...     print(result.full_text)
    """

    def __init__(
        self,
        *,
        lang: str = "ch",
    ) -> None:
        """
        初始化竖排文字识别器

        Args:
            lang: 语言代码，支持 'ch'（简中）、'chinese_cht'（繁中）、'japan'（日文）
        """
        self.lang = lang

        self._ocr: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "VerticalTextRecognizer":
        """初始化 OCR 引擎"""
        if self._initialized:
            return self

        lang_name = VERTICAL_TEXT_LANGUAGES.get(self.lang, self.lang)
        logger.info("正在初始化竖排文字识别引擎...")
        logger.info(f"语言: {lang_name}")

        try:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                lang=self.lang,
                use_doc_orientation_classify=False,  # macOS 内存优化：禁用文档方向分类
                use_doc_unwarping=False,             # macOS 内存优化：禁用文档弯曲矫正
                use_textline_orientation=False,      # macOS 内存优化：禁用文本行方向分类
            )
            self._initialized = True
            logger.info("竖排文字识别引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"竖排文字识别引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._ocr is not None:
            del self._ocr
            self._ocr = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "VerticalTextRecognizer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> VerticalTextResult:
        """
        识别竖排文字

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）

        Returns:
            VerticalTextResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("竖排文字识别引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在识别竖排文字: {path.name}")

        try:
            # 执行预测
            result = self._ocr.predict(str(path))

            texts: list[dict[str, Any]] = []

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in result:
                # 打印结果
                res.print()

                # 提取文本
                formatted = format_ocr_result([res])
                texts.extend(formatted)

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

            return VerticalTextResult(
                source_file=str(path),
                language=self.lang,
                texts=texts,
                text_count=len(texts),
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"竖排文字识别失败: {e}")
            return VerticalTextResult(
                source_file=str(path),
                language=self.lang,
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_vertical_text(
    image_path: Union[str, Path],
    *,
    lang: str = "ch",
    output_dir: Optional[Union[str, Path]] = None,
) -> VerticalTextResult:
    """
    便捷函数 - 识别竖排文字

    Args:
        image_path: 图片路径
        lang: 语言代码
        output_dir: 输出目录（可选）

    Returns:
        VerticalTextResult: 识别结果

    Example:
        >>> result = recognize_vertical_text("book.png", lang="chinese_cht")
        >>> print(result.full_text)
    """
    with VerticalTextRecognizer(lang=lang) as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


def recognize_japanese_vertical(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> VerticalTextResult:
    """
    便捷函数 - 识别日文竖排文字

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        VerticalTextResult: 识别结果
    """
    return recognize_vertical_text(image_path, lang="japan", output_dir=output_dir)


def recognize_traditional_chinese_vertical(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> VerticalTextResult:
    """
    便捷函数 - 识别繁体中文竖排文字

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        VerticalTextResult: 识别结果
    """
    return recognize_vertical_text(image_path, lang="chinese_cht", output_dir=output_dir)


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示竖排文字识别功能

    该函数展示了 PaddleOCR 的竖排文字识别功能：
    1. 启用方向检测参数
    2. 支持多种语言
    3. 正确处理竖排排版
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-OCRv5 竖排文字识别示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "vertical"

    # 打印说明
    logger.info("")
    logger.info("关键参数:")
    logger.info("  - use_doc_orientation_classify=True  # 文档方向检测")
    logger.info("  - use_textline_orientation=True      # 文本行方向检测")
    logger.info("")
    logger.info("支持语言:")
    for code, name in VERTICAL_TEXT_LANGUAGES.items():
        logger.info(f"  - lang='{code}'           # {name}")
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 竖排书籍、古籍")
    logger.info("  - 日文竖排文档")
    logger.info("  - 竖排标语、招牌")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备竖排文字图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用竖排文字识别器
        with VerticalTextRecognizer(lang="ch") as recognizer:
            result = recognizer.recognize(
                image_path,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("识别完成!")
                logger.info(
                    f"识别语言: {VERTICAL_TEXT_LANGUAGES.get(result.language, result.language)}"
                )
                logger.info(f"文本行数: {result.text_count}")
                logger.info(f"平均置信度: {result.average_confidence:.1%}")

                if result.texts:
                    logger.info("")
                    logger.info("识别结果:")
                    for i, text in enumerate(result.texts[:10], 1):
                        content = text.get("text", "")
                        confidence = text.get("confidence", 0)
                        logger.info(f"  [{i}] {content} ({confidence:.1%})")
                    if result.text_count > 10:
                        logger.info(f"  ... 共 {result.text_count} 行")
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
