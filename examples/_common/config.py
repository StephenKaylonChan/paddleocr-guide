#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置常量 - OCR 相关配置参数和常量定义
Configuration Constants - OCR Related Config Parameters and Constants

本模块集中定义了所有 PaddleOCR 示例代码中使用的配置常量，
包括支持的语言、图片格式、默认参数等。通过集中管理配置，
可以避免魔法字符串和硬编码值，提高代码的可维护性。

This module centrally defines all configuration constants used in
PaddleOCR examples, including supported languages, image formats,
and default parameters.

作者: paddleocr-guide
API 版本: PaddleOCR 3.x
"""

from __future__ import annotations

import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, FrozenSet, Optional

# =============================================================================
# 支持的语言代码映射
# Supported Language Code Mapping
# =============================================================================

# PaddleOCR 支持的语言代码及其描述
# 完整列表参考: https://paddleocr.ai/
SUPPORTED_LANGUAGES: dict[str, str] = {
    # 东亚语言 (East Asian Languages)
    "ch": "中文 (Chinese)",
    "chinese_cht": "繁体中文 (Traditional Chinese)",
    "en": "英文 (English)",
    "japan": "日文 (Japanese)",
    "korean": "韩文 (Korean)",
    # 欧洲语言 (European Languages)
    "french": "法语 (French)",
    "german": "德语 (German)",
    "italian": "意大利语 (Italian)",
    "spanish": "西班牙语 (Spanish)",
    "portuguese": "葡萄牙语 (Portuguese)",
    "russian": "俄语 (Russian)",
    "uk": "乌克兰语 (Ukrainian)",
    "be": "白俄罗斯语 (Belarusian)",
    "te": "泰卢固语 (Telugu)",
    "ka": "卡纳达语 (Kannada)",
    "ta": "泰米尔语 (Tamil)",
    "latin": "拉丁语 (Latin)",
    # 中东语言 (Middle Eastern Languages)
    "arabic": "阿拉伯语 (Arabic)",
    "fa": "波斯语 (Persian/Farsi)",
    "ug": "维吾尔语 (Uyghur)",
    # 南亚语言 (South Asian Languages)
    "hi": "印地语 (Hindi)",
    "mr": "马拉地语 (Marathi)",
    "ne": "尼泊尔语 (Nepali)",
    # 东南亚语言 (Southeast Asian Languages)
    "th": "泰语 (Thai)",
    "vi": "越南语 (Vietnamese)",
    "ms": "马来语 (Malay)",
    "id": "印尼语 (Indonesian)",
    # 其他语言 (Other Languages)
    "cyrillic": "西里尔文 (Cyrillic)",
    "devanagari": "天城文 (Devanagari)",
}

# 常用语言快捷映射（别名）
LANGUAGE_ALIASES: dict[str, str] = {
    "chinese": "ch",
    "english": "en",
    "japanese": "japan",
    "korea": "korean",
    "de": "german",
    "fr": "french",
    "es": "spanish",
    "pt": "portuguese",
    "ru": "russian",
    "ar": "arabic",
}


# =============================================================================
# 支持的图片格式
# Supported Image Formats
# =============================================================================

# 支持的图片文件扩展名（小写）
SUPPORTED_IMAGE_EXTENSIONS: FrozenSet[str] = frozenset(
    {
        ".png",  # PNG 格式 - 推荐，无损压缩
        ".jpg",  # JPEG 格式 - 常用，有损压缩
        ".jpeg",  # JPEG 格式 - 同上
        ".bmp",  # BMP 格式 - 无压缩位图
        ".tiff",  # TIFF 格式 - 专业图像格式
        ".tif",  # TIFF 格式 - 同上
        ".webp",  # WebP 格式 - 现代网页格式
        ".gif",  # GIF 格式 - 支持但不推荐（可能是动图）
    }
)

# 支持的文档格式
SUPPORTED_DOCUMENT_EXTENSIONS: FrozenSet[str] = frozenset(
    {
        ".pdf",  # PDF 文档
    }
)

# 所有支持的输入格式
ALL_SUPPORTED_EXTENSIONS: FrozenSet[str] = (
    SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_DOCUMENT_EXTENSIONS
)


# =============================================================================
# 默认参数配置
# Default Parameter Configuration
# =============================================================================


@dataclass(frozen=True)
class OCRDefaults:
    """
    OCR 默认参数配置类

    该类定义了 PaddleOCR 引擎的默认参数值。
    使用 dataclass 和 frozen=True 确保配置不可变。

    Attributes:
        lang: 默认语言代码
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正
        use_textline_orientation: 是否启用文本行方向分类
        text_det_limit_side_len: 检测图像边长限制
        text_det_thresh: 文本检测阈值
        text_rec_score_thresh: 文本识别置信度阈值

    Example:
        >>> defaults = OCRDefaults()
        >>> print(defaults.lang)
        'ch'
        >>> print(defaults.text_det_thresh)
        0.3
    """

    # 语言设置
    lang: str = "ch"

    # 文档预处理选项
    use_doc_orientation_classify: bool = False
    use_doc_unwarping: bool = False
    use_textline_orientation: bool = False

    # 检测参数
    text_det_limit_side_len: int = 960
    text_det_thresh: float = 0.3
    text_det_box_thresh: float = 0.6
    text_det_unclip_ratio: float = 1.5

    # 识别参数
    text_rec_score_thresh: float = 0.5

    # 批处理参数
    text_det_batch_size: int = 1
    text_rec_batch_size: int = 8


@dataclass(frozen=True)
class StructureDefaults:
    """
    PP-StructureV3 默认参数配置类

    该类定义了文档结构分析的默认参数值。

    Attributes:
        use_table_recognition: 是否启用表格识别
        use_seal_recognition: 是否启用印章识别
        use_formula_recognition: 是否启用公式识别
        use_chart_recognition: 是否启用图表识别
        use_layout_detection: 是否启用版面检测
    """

    use_table_recognition: bool = True
    use_seal_recognition: bool = False
    use_formula_recognition: bool = False
    use_chart_recognition: bool = False
    use_layout_detection: bool = True

    # 版面检测参数
    layout_batch_size: int = 1
    layout_score_threshold: float = 0.5


# =============================================================================
# 路径配置
# Path Configuration
# =============================================================================


@dataclass
class PathConfig:
    """
    路径配置类 - 管理项目相关路径

    该类根据项目结构自动计算各种路径，
    包括输入目录、输出目录、资源目录等。

    Attributes:
        project_root: 项目根目录
        examples_dir: 示例代码目录
        assets_dir: 资源目录
        test_images_dir: 测试图片目录
        outputs_dir: 输出目录

    Example:
        >>> config = PathConfig()
        >>> print(config.test_images_dir)
        PosixPath('/path/to/project/assets/test_images')
    """

    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)

    @property
    def examples_dir(self) -> Path:
        """示例代码目录"""
        return self.project_root / "examples"

    @property
    def assets_dir(self) -> Path:
        """资源目录"""
        return self.project_root / "assets"

    @property
    def test_images_dir(self) -> Path:
        """测试图片目录"""
        return self.assets_dir / "test_images"

    @property
    def outputs_dir(self) -> Path:
        """输出目录"""
        return self.assets_dir / "outputs"

    @property
    def docs_dir(self) -> Path:
        """文档目录"""
        return self.project_root / "docs"

    def ensure_output_dir(self) -> Path:
        """
        确保输出目录存在，如果不存在则创建

        Returns:
            Path: 输出目录路径

        Raises:
            OSError: 如果无法创建目录
        """
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        return self.outputs_dir


# =============================================================================
# 平台检测
# Platform Detection
# =============================================================================


@dataclass(frozen=True)
class PlatformInfo:
    """
    平台信息类 - 检测当前运行环境

    该类用于检测当前运行平台，判断功能兼容性。
    特别重要的是检测 macOS ARM 芯片，因为某些功能（如 PaddleOCR-VL）不支持。

    Attributes:
        system: 操作系统名称 (Darwin/Linux/Windows)
        machine: CPU 架构 (arm64/x86_64/AMD64)
        is_macos: 是否为 macOS
        is_macos_arm: 是否为 macOS ARM 芯片
        is_linux: 是否为 Linux
        is_windows: 是否为 Windows

    Example:
        >>> info = PlatformInfo()
        >>> if info.is_macos_arm:
        ...     print("警告: PaddleOCR-VL 不支持 macOS ARM")
    """

    system: str = field(default_factory=platform.system)
    machine: str = field(default_factory=platform.machine)

    @property
    def is_macos(self) -> bool:
        """是否为 macOS 系统"""
        return self.system == "Darwin"

    @property
    def is_macos_arm(self) -> bool:
        """
        是否为 macOS ARM 芯片 (M1/M2/M3/M4)

        重要：PaddleOCR-VL 不支持此平台！
        """
        return self.is_macos and self.machine == "arm64"

    @property
    def is_linux(self) -> bool:
        """是否为 Linux 系统"""
        return self.system == "Linux"

    @property
    def is_windows(self) -> bool:
        """是否为 Windows 系统"""
        return self.system == "Windows"

    @property
    def supports_paddleocr_vl(self) -> bool:
        """
        是否支持 PaddleOCR-VL

        PaddleOCR-VL 需要特定的硬件支持，不支持 macOS ARM。
        """
        return not self.is_macos_arm

    def get_platform_string(self) -> str:
        """获取平台描述字符串"""
        return f"{self.system} {self.machine}"


# =============================================================================
# 输出格式
# Output Formats
# =============================================================================


class OutputFormat:
    """输出格式常量"""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"
    TXT = "txt"
    XLSX = "xlsx"

    # 所有支持的格式
    ALL: FrozenSet[str] = frozenset({JSON, MARKDOWN, HTML, CSV, TXT, XLSX})

    # 文档格式
    DOCUMENT_FORMATS: FrozenSet[str] = frozenset({MARKDOWN, HTML, TXT})

    # 数据格式
    DATA_FORMATS: FrozenSet[str] = frozenset({JSON, CSV, XLSX})


# =============================================================================
# 全局配置实例
# Global Configuration Instances
# =============================================================================

# 默认 OCR 参数
DEFAULT_OCR_CONFIG = OCRDefaults()

# 默认结构分析参数
DEFAULT_STRUCTURE_CONFIG = StructureDefaults()

# 路径配置
PATH_CONFIG = PathConfig()

# 平台信息
PLATFORM_INFO = PlatformInfo()


# =============================================================================
# 便捷函数
# Utility Functions
# =============================================================================


def is_supported_language(lang: str) -> bool:
    """
    检查语言代码是否支持

    Args:
        lang: 语言代码

    Returns:
        bool: 是否支持该语言
    """
    # 检查直接语言代码
    if lang in SUPPORTED_LANGUAGES:
        return True
    # 检查别名
    if lang in LANGUAGE_ALIASES:
        return True
    return False


def normalize_language(lang: str) -> str:
    """
    标准化语言代码（处理别名）

    Args:
        lang: 语言代码或别名

    Returns:
        str: 标准化的语言代码

    Raises:
        ValueError: 如果语言不支持
    """
    # 先尝试小写形式
    lang_lower = lang.lower()

    if lang_lower in SUPPORTED_LANGUAGES:
        return lang_lower
    if lang in SUPPORTED_LANGUAGES:
        return lang
    if lang_lower in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[lang_lower]
    if lang in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[lang]
    raise ValueError(f"不支持的语言: {lang}")


def is_supported_image(file_path: str | Path) -> bool:
    """
    检查文件是否为支持的图片格式

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为支持的图片格式
    """
    suffix = Path(file_path).suffix.lower()
    return suffix in SUPPORTED_IMAGE_EXTENSIONS


def is_supported_document(file_path: str | Path) -> bool:
    """
    检查文件是否为支持的文档格式

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为支持的文档格式
    """
    suffix = Path(file_path).suffix.lower()
    return suffix in SUPPORTED_DOCUMENT_EXTENSIONS


def is_supported_input(file_path: str | Path) -> bool:
    """
    检查文件是否为支持的输入格式（图片或文档）

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为支持的输入格式
    """
    return is_supported_image(file_path) or is_supported_document(file_path)
