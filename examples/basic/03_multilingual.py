#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言 OCR 示例 - 识别不同语言的文字
Multilingual OCR Example - Recognize Text in Different Languages

本示例演示了 PaddleOCR 的多语言识别能力，包括：
- 指定语言识别
- 自动语言检测
- 中英文混合识别

PaddleOCR 支持 80+ 种语言，涵盖拉丁语系、阿拉伯语系、
西里尔语系、天城文、中日韩等多种文字系统。

This example demonstrates PaddleOCR's multilingual recognition
capabilities, including specified language recognition, automatic
language detection, and mixed Chinese-English recognition.

适用模型: PP-OCRv5 (默认，~10MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/basic/03_multilingual.py

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
    OCRConfigError,
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    format_ocr_result,
    get_logger,
    is_supported_language,
    normalize_language,
    setup_logging,
)

# 配置模块日志器
logger = get_logger(__name__)


# =============================================================================
# 常用语言分组
# Common Language Groups
# =============================================================================

# 东亚语言（最常用）
EAST_ASIAN_LANGUAGES = {
    "ch": "中文（简体+繁体+英文）",
    "chinese_cht": "繁体中文",
    "en": "英文",
    "japan": "日文",
    "korean": "韩文",
}

# 欧洲语言
EUROPEAN_LANGUAGES = {
    "latin": "拉丁语系",
    "french": "法语",
    "german": "德语",
    "italian": "意大利语",
    "spanish": "西班牙语",
    "portuguese": "葡萄牙语",
    "russian": "俄语",
    "cyrillic": "西里尔语系",
}

# 中东和南亚语言
MIDDLE_EAST_SOUTH_ASIAN_LANGUAGES = {
    "arabic": "阿拉伯语",
    "fa": "波斯语",
    "hi": "印地语",
    "devanagari": "天城文",
    "ta": "泰米尔语",
    "te": "泰卢固语",
    "ka": "卡纳达语",
}

# 所有常用语言的合集
ALL_COMMON_LANGUAGES = {
    **EAST_ASIAN_LANGUAGES,
    **EUROPEAN_LANGUAGES,
    **MIDDLE_EAST_SOUTH_ASIAN_LANGUAGES,
}


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class LanguageResult:
    """
    单语言识别结果

    Attributes:
        language_code: 语言代码
        language_name: 语言名称
        texts: 识别的文本列表
        average_confidence: 平均置信度
        text_count: 文本行数
    """

    language_code: str
    language_name: str
    texts: list[dict[str, Any]] = field(default_factory=list)
    average_confidence: float = 0.0
    text_count: int = 0
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """是否识别成功"""
        return self.error is None and self.text_count > 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "language": self.language_code,
            "language_name": self.language_name,
            "text_count": self.text_count,
            "average_confidence": self.average_confidence,
            "texts": self.texts,
            "error": self.error,
        }


@dataclass
class AutoDetectResult:
    """
    自动语言检测结果

    Attributes:
        best_match: 最佳匹配语言
        all_results: 所有尝试的语言结果
    """

    best_match: Optional[LanguageResult] = None
    all_results: list[LanguageResult] = field(default_factory=list)

    @property
    def detected_language(self) -> Optional[str]:
        """检测到的最佳语言代码"""
        return self.best_match.language_code if self.best_match else None


# =============================================================================
# 多语言 OCR 处理器类
# Multilingual OCR Processor Class
# =============================================================================


class MultilingualOCR:
    """
    多语言 OCR 处理器

    该类封装了多语言 OCR 识别功能，支持：
    - 指定语言识别
    - 自动语言检测
    - OCR 引擎缓存（避免重复初始化）

    通过缓存已初始化的 OCR 引擎，可以显著提高多语言识别的效率。

    Attributes:
        _engine_cache: OCR 引擎缓存字典

    Example:
        >>> with MultilingualOCR() as ocr:
        ...     # 指定语言识别
        ...     result = ocr.recognize("image.png", lang="japan")
        ...
        ...     # 自动检测语言
        ...     auto_result = ocr.auto_detect("image.png")
        ...     print(f"检测到语言: {auto_result.detected_language}")
    """

    def __init__(self) -> None:
        """初始化多语言处理器"""
        self._engine_cache: dict[str, Any] = {}
        logger.debug("MultilingualOCR 初始化")

    def _get_or_create_engine(self, lang: str) -> Any:
        """
        获取或创建指定语言的 OCR 引擎

        使用缓存避免重复初始化，提高效率。

        Args:
            lang: 语言代码

        Returns:
            PaddleOCR: OCR 引擎实例

        Raises:
            OCRConfigError: 不支持的语言
            OCRInitError: 引擎初始化失败
        """
        # 检查语言是否支持
        if not is_supported_language(lang):
            raise OCRConfigError(
                f"不支持的语言: {lang}",
                details={"supported_languages": list(SUPPORTED_LANGUAGES.keys())},
            )

        # 标准化语言代码
        normalized_lang = normalize_language(lang)

        # 检查缓存
        if normalized_lang in self._engine_cache:
            logger.debug(f"使用缓存的 OCR 引擎: {normalized_lang}")
            return self._engine_cache[normalized_lang]

        # 创建新引擎
        logger.info(f"正在初始化 OCR 引擎: {normalized_lang}")
        try:
            from paddleocr import PaddleOCR

            engine = PaddleOCR(
                lang=normalized_lang,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            self._engine_cache[normalized_lang] = engine
            logger.debug(f"OCR 引擎已缓存: {normalized_lang}")
            return engine

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"OCR 引擎初始化失败: {e}",
                error_code="E101",
                details={"lang": normalized_lang},
            ) from e

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        lang: str = "ch",
        min_confidence: float = 0.0,
    ) -> LanguageResult:
        """
        使用指定语言识别图片

        Args:
            image_path: 图片路径
            lang: 语言代码，默认 'ch'
            min_confidence: 最低置信度阈值

        Returns:
            LanguageResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRConfigError: 不支持的语言
        """
        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"图片不存在: {path}",
                file_path=str(path),
            )

        # 获取语言名称
        lang_name = SUPPORTED_LANGUAGES.get(lang, ALL_COMMON_LANGUAGES.get(lang, lang))

        logger.info(f"识别语言: {lang_name} ({lang})")

        try:
            # 获取或创建引擎
            engine = self._get_or_create_engine(lang)

            # 执行识别
            result = engine.predict(str(path))

            # 格式化结果
            texts = format_ocr_result(result, min_confidence=min_confidence)

            # 计算平均置信度
            if texts:
                avg_conf = sum(t.get("confidence", 0) for t in texts) / len(texts)
            else:
                avg_conf = 0.0

            return LanguageResult(
                language_code=lang,
                language_name=lang_name,
                texts=texts,
                average_confidence=avg_conf,
                text_count=len(texts),
            )

        except OCRException:
            raise
        except Exception as e:
            logger.warning(f"识别失败 ({lang}): {e}")
            return LanguageResult(
                language_code=lang,
                language_name=lang_name,
                error=str(e),
            )

    def auto_detect(
        self,
        image_path: Union[str, Path],
        *,
        candidates: Optional[list[str]] = None,
        min_confidence: float = 0.0,
    ) -> AutoDetectResult:
        """
        自动检测图片语言

        通过尝试多种语言识别，选择平均置信度最高的结果。

        Args:
            image_path: 图片路径
            candidates: 候选语言列表，默认 ['ch', 'en', 'japan', 'korean']
            min_confidence: 最低置信度阈值

        Returns:
            AutoDetectResult: 自动检测结果

        Note:
            该方法会依次尝试每种候选语言，可能较慢。
            建议在已知可能的语言范围时指定 candidates 参数。
        """
        if candidates is None:
            candidates = ["ch", "en", "japan", "korean"]

        logger.info(f"自动检测语言，候选: {candidates}")

        all_results: list[LanguageResult] = []
        best_result: Optional[LanguageResult] = None
        best_confidence: float = 0.0

        for lang in candidates:
            lang_name = ALL_COMMON_LANGUAGES.get(lang, lang)
            logger.info(f"  尝试: {lang_name}")

            result = self.recognize(image_path, lang=lang, min_confidence=min_confidence)
            all_results.append(result)

            if result.is_success:
                logger.info(
                    f"    文本数: {result.text_count}, 置信度: {result.average_confidence:.2%}"
                )

                if result.average_confidence > best_confidence:
                    best_confidence = result.average_confidence
                    best_result = result
            else:
                logger.info(f"    识别失败: {result.error}")

        if best_result:
            logger.info(f"最佳匹配: {best_result.language_name} (置信度: {best_confidence:.2%})")

        return AutoDetectResult(
            best_match=best_result,
            all_results=all_results,
        )

    def cleanup(self) -> None:
        """清理所有缓存的 OCR 引擎"""
        logger.debug("正在清理多语言 OCR 缓存...")
        for lang, engine in self._engine_cache.items():
            logger.debug(f"  清理引擎: {lang}")
            del engine
        self._engine_cache.clear()
        gc.collect()
        logger.debug("多语言 OCR 缓存清理完成")

    def __enter__(self) -> "MultilingualOCR":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def print_supported_languages() -> None:
    """
    打印支持的语言列表

    分组显示所有常用的语言代码和名称。
    """
    logger.info("=" * 50)
    logger.info("PaddleOCR 支持的语言列表")
    logger.info("=" * 50)

    logger.info("")
    logger.info("【东亚语言】")
    for code, name in EAST_ASIAN_LANGUAGES.items():
        logger.info(f"  {code:15} - {name}")

    logger.info("")
    logger.info("【欧洲语言】")
    for code, name in EUROPEAN_LANGUAGES.items():
        logger.info(f"  {code:15} - {name}")

    logger.info("")
    logger.info("【中东和南亚语言】")
    for code, name in MIDDLE_EAST_SOUTH_ASIAN_LANGUAGES.items():
        logger.info(f"  {code:15} - {name}")

    logger.info("")
    logger.info("完整语言列表请参考: https://paddleocr.ai/")


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示多语言 OCR 功能

    该函数展示了三种多语言识别场景：
    1. 中文识别（默认，支持中英混合）
    2. 自动语言检测
    3. 中英混合识别说明
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 50)
    logger.info("PaddleOCR 多语言识别示例")
    logger.info("=" * 50)

    # 打印支持的语言
    print_supported_languages()

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"

    # 检查测试图片
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请将测试图片放入以下目录:")
        logger.info(f"  {PATH_CONFIG.test_images_dir}")
        return

    try:
        with MultilingualOCR() as ocr:
            # 示例 1: 中文识别
            logger.info("")
            logger.info("【示例 1】中文识别")
            logger.info("-" * 30)

            result = ocr.recognize(image_path, lang="ch")

            if result.is_success:
                logger.info(f"识别到 {result.text_count} 行文字")
                logger.info(f"平均置信度: {result.average_confidence:.2%}")

                # 显示前 5 行
                for i, text in enumerate(result.texts[:5]):
                    logger.info(f"  {text['text']} ({text['confidence']:.2%})")

                if result.text_count > 5:
                    logger.info(f"  ... 共 {result.text_count} 行")
            else:
                logger.warning(f"识别失败: {result.error}")

            # 示例 2: 自动检测语言
            logger.info("")
            logger.info("【示例 2】自动检测语言")
            logger.info("-" * 30)

            auto_result = ocr.auto_detect(image_path)

            if auto_result.best_match:
                logger.info(f"检测到语言: {auto_result.best_match.language_name}")
                logger.info(f"置信度: {auto_result.best_match.average_confidence:.2%}")

            # 示例 3: 中英混合说明
            logger.info("")
            logger.info("【示例 3】中英混合识别说明")
            logger.info("-" * 30)
            logger.info("lang='ch' 默认支持中英文混合识别")
            logger.info("无需单独处理英文内容")
            logger.info("如需纯英文识别，可使用 lang='en'")

    except OCRFileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        raise SystemExit(1) from e

    except OCRConfigError as e:
        logger.error(f"配置错误: {e}")
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
