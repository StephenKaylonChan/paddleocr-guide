#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档翻译示例 - 使用 PP-DocTranslation
Document Translation Example - Using PP-DocTranslation

本示例演示了如何使用 PP-DocTranslation 进行文档翻译。
PP-DocTranslation 可以保持文档的版面结构进行翻译。

⚠️ 重要提示：
   翻译功能需要配置 LLM API（如 ERNIE API）
   本示例演示视觉分析部分，完整翻译需要 API Key

支持的语言对：
- 中文 ↔ 英文
- 中文 ↔ 日文
- 中文 ↔ 韩文
- 更多语言组合...

This example demonstrates how to use PP-DocTranslation for
document translation. Note that the translation feature requires
an LLM API configuration.

适用模型: PP-DocTranslation
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/09_doc_translation.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import gc
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples._common import (  # 异常类; 日志; 配置; 工具函数
    PATH_CONFIG,
    OCRConfigError,
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
# 支持的语言常量
# Supported Language Constants
# =============================================================================

# 支持的翻译语言
SUPPORTED_TRANSLATION_LANGUAGES = {
    "zh": "中文",
    "en": "英文",
    "ja": "日文",
    "ko": "韩文",
    "fr": "法文",
    "de": "德文",
    "es": "西班牙文",
    "ru": "俄文",
}


# =============================================================================
# LLM 配置
# LLM Configuration
# =============================================================================


@dataclass
class LLMConfig:
    """
    LLM 配置

    用于配置翻译所需的大语言模型 API。

    Attributes:
        module_name: 模块名称
        model_name: 模型名称
        base_url: API 基础 URL
        api_type: API 类型
        api_key: API 密钥（可从环境变量读取）
    """

    module_name: str = "chat_bot"
    model_name: str = "ernie-3.5-8k"
    base_url: str = "https://qianfan.baidubce.com/v2"
    api_type: str = "openai"
    api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """从环境变量创建配置"""
        api_key = os.environ.get("QIANFAN_API_KEY")
        return cls(api_key=api_key)

    @property
    def has_api_key(self) -> bool:
        """是否有 API Key"""
        return self.api_key is not None and len(self.api_key) > 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于 API 调用）"""
        return {
            "module_name": self.module_name,
            "model_name": self.model_name,
            "base_url": self.base_url,
            "api_type": self.api_type,
            "api_key": self.api_key,
        }


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class TranslationResult:
    """
    文档翻译结果

    Attributes:
        source_file: 源文件路径
        source_lang: 源语言
        target_lang: 目标语言
        visual_analysis_done: 视觉分析是否完成
        translation_done: 翻译是否完成
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    source_lang: str = "en"
    target_lang: str = "zh"
    visual_analysis_done: bool = False
    translation_done: bool = False
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "visual_analysis_done": self.visual_analysis_done,
            "translation_done": self.translation_done,
            "page_count": self.page_count,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 文档翻译器类
# Document Translator Class
# =============================================================================


class DocumentTranslator:
    """
    文档翻译器 - 保持版面结构的文档翻译

    该类封装了 PP-DocTranslation 的文档翻译功能，支持：
    - 视觉分析（识别文档结构）
    - 保持版面结构的翻译
    - 多种语言对

    ⚠️ 翻译功能需要配置 LLM API（如 ERNIE API）。
    本类提供视觉分析功能，完整翻译需要 API Key。

    Attributes:
        source_lang: 源语言代码
        target_lang: 目标语言代码
        llm_config: LLM 配置

    Example:
        >>> # 仅视觉分析（不需要 API Key）
        >>> with DocumentTranslator() as translator:
        ...     result = translator.visual_analyze("english_doc.png")
        ...     print(f"分析完成: {result.visual_analysis_done}")
        ...
        >>> # 完整翻译（需要 API Key）
        >>> config = LLMConfig(api_key="your_api_key")
        >>> with DocumentTranslator(llm_config=config) as translator:
        ...     result = translator.translate("english_doc.png")
    """

    def __init__(
        self,
        *,
        source_lang: str = "en",
        target_lang: str = "zh",
        llm_config: Optional[LLMConfig] = None,
    ) -> None:
        """
        初始化文档翻译器

        Args:
            source_lang: 源语言代码（en/zh/ja/ko 等）
            target_lang: 目标语言代码
            llm_config: LLM 配置（可选，用于完整翻译）
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.llm_config = llm_config or LLMConfig.from_env()

        self._translator: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "DocumentTranslator":
        """初始化 PP-DocTranslation 引擎"""
        if self._initialized:
            return self

        source_name = SUPPORTED_TRANSLATION_LANGUAGES.get(self.source_lang, self.source_lang)
        target_name = SUPPORTED_TRANSLATION_LANGUAGES.get(self.target_lang, self.target_lang)

        logger.info("正在初始化文档翻译引擎...")
        logger.info(f"翻译方向: {source_name} → {target_name}")

        if self.llm_config.has_api_key:
            logger.info("LLM API: 已配置")
        else:
            logger.info("LLM API: 未配置（仅支持视觉分析）")

        try:
            from paddleocr import PPDocTranslation

            # 构建配置
            chat_bot_config = self.llm_config.to_dict() if self.llm_config.has_api_key else None

            self._translator = PPDocTranslation(
                use_doc_orientation_classify=True,
                use_doc_unwarping=False,
                use_table_recognition=True,
                use_seal_recognition=False,
                chat_bot_config=chat_bot_config,
            )
            self._initialized = True
            logger.info("文档翻译引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"文档翻译引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._translator is not None:
            del self._translator
            self._translator = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "DocumentTranslator":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def visual_analyze(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> TranslationResult:
        """
        执行视觉分析（不需要 API Key）

        分析文档的版面结构，为后续翻译做准备。

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）

        Returns:
            TranslationResult: 分析结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("文档翻译引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        source_name = SUPPORTED_TRANSLATION_LANGUAGES.get(self.source_lang, self.source_lang)
        target_name = SUPPORTED_TRANSLATION_LANGUAGES.get(self.target_lang, self.target_lang)

        logger.info(f"正在分析文档: {path.name}")
        logger.info(f"翻译方向: {source_name} → {target_name}")

        try:
            # 执行视觉分析
            visual_results = self._translator.visual_predict(input=str(path))

            page_count = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in visual_results:
                page_count += 1

                # 打印版面分析结果
                if "layout_parsing_result" in res:
                    res["layout_parsing_result"].print()

                    # 保存结果
                    if output_dir:
                        try:
                            res["layout_parsing_result"].save_to_markdown(
                                save_path=str(output_path)
                            )
                            res["layout_parsing_result"].save_to_json(save_path=str(output_path))
                        except Exception as e:
                            logger.warning(f"保存结果时出错: {e}")

            logger.info(f"视觉分析完成，共处理 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return TranslationResult(
                source_file=str(path),
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                visual_analysis_done=True,
                translation_done=False,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"视觉分析失败: {e}")
            return TranslationResult(
                source_file=str(path),
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def analyze_for_translation(
    image_path: Union[str, Path],
    *,
    source_lang: str = "en",
    target_lang: str = "zh",
    output_dir: Optional[Union[str, Path]] = None,
) -> TranslationResult:
    """
    便捷函数 - 分析文档用于翻译

    执行视觉分析，为后续翻译做准备。
    此功能不需要 API Key。

    Args:
        image_path: 图片路径
        source_lang: 源语言
        target_lang: 目标语言
        output_dir: 输出目录（可选）

    Returns:
        TranslationResult: 分析结果

    Example:
        >>> result = analyze_for_translation("english_doc.png")
        >>> print(f"分析完成: {result.visual_analysis_done}")
    """
    with DocumentTranslator(source_lang=source_lang, target_lang=target_lang) as translator:
        return translator.visual_analyze(image_path, output_dir=output_dir)


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示文档翻译功能

    该函数展示了 PP-DocTranslation 的功能：
    1. 视觉分析（不需要 API Key）
    2. 翻译功能说明（需要 API Key）
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-DocTranslation 文档翻译示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "translation"

    # 打印说明
    logger.info("")
    logger.info("功能说明:")
    logger.info("  - 识别文档内容（文字、表格、图片）")
    logger.info("  - 保持版面结构进行翻译")
    logger.info("  - 支持多种语言对")
    logger.info("")
    logger.info("支持的语言:")
    for code, name in SUPPORTED_TRANSLATION_LANGUAGES.items():
        logger.info(f"  - {code}: {name}")
    logger.info("")
    logger.info("⚠️ 注意:")
    logger.info("  - 翻译功能需要配置 LLM API")
    logger.info("  - 推荐使用 ERNIE API 或其他兼容 OpenAI 格式的 API")
    logger.info("  - 设置环境变量: export QIANFAN_API_KEY=your_key")
    logger.info("")

    # 检查 API Key
    llm_config = LLMConfig.from_env()
    if llm_config.has_api_key:
        logger.info("✅ 已检测到 API Key，可使用完整翻译功能")
    else:
        logger.info("⚠️  未检测到 API Key，仅演示视觉分析功能")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备需要翻译的文档图片")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 视觉分析模式
        logger.info("【视觉分析模式】")
        logger.info("（翻译功能需要配置 API Key）")
        logger.info("")

        with DocumentTranslator() as translator:
            result = translator.visual_analyze(
                image_path,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("视觉分析完成!")
                logger.info(f"共处理 {result.page_count} 页")
                logger.info(f"视觉分析: {'完成' if result.visual_analysis_done else '未完成'}")
                logger.info(f"翻译: {'完成' if result.translation_done else '未完成'}")
                logger.info("")

                if not llm_config.has_api_key:
                    logger.info("要启用完整翻译功能，请:")
                    logger.info("  1. 获取 ERNIE API Key")
                    logger.info("  2. 设置环境变量: export QIANFAN_API_KEY=your_key")
                    logger.info("  3. 或在代码中配置 LLMConfig")
            else:
                logger.error(f"分析失败: {result.error}")

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
