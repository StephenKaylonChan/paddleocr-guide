#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数 - 通用辅助函数集合
Utility Functions - Common Helper Function Collection

本模块提供了各种通用的辅助函数，用于：
- 文件操作（读取、保存、格式转换）
- 图像处理（验证、预处理）
- 结果处理（格式化、导出）
- 其他常用操作

这些函数被设计为无状态的纯函数，便于复用和测试。

This module provides various utility functions for:
- File operations (reading, saving, format conversion)
- Image processing (validation, preprocessing)
- Result processing (formatting, exporting)
- Other common operations

作者: paddleocr-guide
API 版本: PaddleOCR 3.x
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence, Union

from .config import (
    ALL_SUPPORTED_EXTENSIONS,
    PATH_CONFIG,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from .exceptions import OCRFileNotFoundError, OCROutputError
from .logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# 文件操作函数
# File Operation Functions
# =============================================================================


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建

    Args:
        path: 目录路径

    Returns:
        Path: 创建或已存在的目录路径

    Raises:
        OCROutputError: 如果无法创建目录

    Example:
        >>> output_dir = ensure_directory("./outputs")
        >>> print(output_dir.exists())
        True
    """
    dir_path = Path(path)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    except PermissionError as e:
        raise OCROutputError(
            f"无权限创建目录: {dir_path}",
            output_path=str(dir_path),
            error_code="E502",
        ) from e
    except OSError as e:
        raise OCROutputError(
            f"创建目录失败: {e}",
            output_path=str(dir_path),
        ) from e


def validate_file_exists(file_path: Union[str, Path]) -> Path:
    """
    验证文件存在

    Args:
        file_path: 文件路径

    Returns:
        Path: 验证后的路径对象

    Raises:
        OCRFileNotFoundError: 文件不存在时抛出
    """
    path = Path(file_path)
    if not path.exists():
        raise OCRFileNotFoundError(
            f"文件不存在: {path}",
            file_path=str(path),
        )
    if not path.is_file():
        raise OCRFileNotFoundError(
            f"路径不是文件: {path}",
            file_path=str(path),
        )
    return path


def find_images(
    directory: Union[str, Path],
    *,
    recursive: bool = False,
    extensions: Optional[set[str]] = None,
) -> Iterator[Path]:
    """
    查找目录中的所有图片文件

    Args:
        directory: 搜索目录
        recursive: 是否递归搜索子目录
        extensions: 允许的扩展名集合，默认使用 SUPPORTED_IMAGE_EXTENSIONS

    Yields:
        Path: 找到的图片文件路径

    Example:
        >>> for image in find_images("./test_images", recursive=True):
        ...     print(image)
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.warning(f"目录不存在: {dir_path}")
        return

    if extensions is None:
        extensions = set(SUPPORTED_IMAGE_EXTENSIONS)

    pattern = "**/*" if recursive else "*"

    for file_path in dir_path.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            yield file_path


def get_output_path(
    input_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    suffix: str = "",
    extension: str = ".txt",
) -> Path:
    """
    根据输入路径生成输出路径

    Args:
        input_path: 输入文件路径
        output_dir: 输出目录，默认使用配置的输出目录
        suffix: 文件名后缀
        extension: 输出文件扩展名

    Returns:
        Path: 生成的输出路径

    Example:
        >>> get_output_path("image.png", suffix="_result", extension=".json")
        PosixPath('assets/outputs/image_result.json')
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir) if output_dir else PATH_CONFIG.outputs_dir

    # 确保输出目录存在
    ensure_directory(output_dir)

    # 生成输出文件名
    output_name = f"{input_path.stem}{suffix}{extension}"
    return output_dir / output_name


# =============================================================================
# JSON 操作函数
# JSON Operation Functions
# =============================================================================


def save_json(
    data: Any,
    file_path: Union[str, Path],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """
    保存数据为 JSON 文件

    Args:
        data: 要保存的数据
        file_path: 输出文件路径
        indent: 缩进空格数
        ensure_ascii: 是否转义非 ASCII 字符

    Raises:
        OCROutputError: 保存失败时抛出

    Example:
        >>> save_json({"text": "你好"}, "result.json")
    """
    path = Path(file_path)
    ensure_directory(path.parent)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        logger.info(f"JSON 已保存: {path}")
    except (IOError, OSError) as e:
        raise OCROutputError(
            f"保存 JSON 失败: {e}",
            output_path=str(path),
        ) from e


def load_json(file_path: Union[str, Path]) -> Any:
    """
    加载 JSON 文件

    Args:
        file_path: JSON 文件路径

    Returns:
        Any: 解析后的数据

    Raises:
        OCRFileNotFoundError: 文件不存在
        ValueError: JSON 解析失败
    """
    path = validate_file_exists(file_path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}") from e


# =============================================================================
# 文本处理函数
# Text Processing Functions
# =============================================================================


def format_ocr_result(
    result: Any,
    *,
    include_confidence: bool = True,
    min_confidence: float = 0.0,
) -> list[dict[str, Any]]:
    """
    格式化 OCR 结果为统一格式

    将 PaddleOCR 的原始结果转换为易于使用的字典列表。

    Args:
        result: PaddleOCR 返回的结果
        include_confidence: 是否包含置信度
        min_confidence: 最低置信度过滤阈值

    Returns:
        list[dict]: 格式化后的结果列表

    Example:
        >>> result = ocr.predict('image.png')
        >>> formatted = format_ocr_result(result)
        >>> for item in formatted:
        ...     print(f"{item['text']} ({item['confidence']:.2f})")
    """
    # 处理空结果
    if result is None:
        return []

    formatted_results = []

    # 处理可迭代结果
    try:
        result_iter = iter(result)
    except TypeError:
        return []

    for res in result_iter:
        try:
            res_json = res.json
            if "rec_texts" in res_json and "rec_scores" in res_json:
                for text, score in zip(res_json["rec_texts"], res_json["rec_scores"]):
                    confidence = float(score)

                    # 置信度过滤
                    if confidence < min_confidence:
                        continue

                    item = {"text": text}
                    if include_confidence:
                        item["confidence"] = confidence

                    formatted_results.append(item)
        except Exception as e:
            logger.warning(f"格式化结果时出错: {e}")
            continue

    return formatted_results


def extract_text_only(result: Any) -> list[str]:
    """
    仅提取文本内容（不含置信度）

    Args:
        result: PaddleOCR 返回的结果

    Returns:
        list[str]: 文本列表
    """
    formatted = format_ocr_result(result, include_confidence=False)
    return [item["text"] for item in formatted]


def join_texts(
    texts: Sequence[Union[str, dict[str, Any]]],
    separator: str = "\n",
) -> str:
    """
    拼接文本列表

    Args:
        texts: 文本列表（可以是字符串或包含 'text' 键的字典）
        separator: 分隔符

    Returns:
        str: 拼接后的文本
    """
    result = []
    for item in texts:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and "text" in item:
            result.append(item["text"])
    return separator.join(result)


def clean_text(
    text: str,
    *,
    remove_whitespace: bool = False,
    remove_special_chars: bool = False,
) -> str:
    """
    清理文本

    Args:
        text: 原始文本
        remove_whitespace: 是否移除多余空白
        remove_special_chars: 是否移除特殊字符

    Returns:
        str: 清理后的文本
    """
    if remove_whitespace:
        # 将多个空白字符替换为单个空格
        text = re.sub(r"\s+", " ", text).strip()

    if remove_special_chars:
        # 移除常见的控制字符，保留中文、英文、数字和标点
        text = re.sub(r"[^\w\s\u4e00-\u9fff，。！？、；：" "''（）【】]", "", text)

    return text


# =============================================================================
# 时间和统计函数
# Time and Statistics Functions
# =============================================================================


def get_timestamp() -> str:
    """
    获取当前时间戳字符串

    Returns:
        str: 格式为 'YYYYMMDD_HHMMSS' 的时间戳
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_file_stats(file_path: Union[str, Path]) -> dict[str, Any]:
    """
    获取文件统计信息

    Args:
        file_path: 文件路径

    Returns:
        dict: 包含文件大小、修改时间等信息
    """
    path = Path(file_path)
    stat = path.stat()

    return {
        "name": path.name,
        "size_bytes": stat.st_size,
        "size_readable": format_file_size(stat.st_size),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "extension": path.suffix.lower(),
    }


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为可读字符串

    Args:
        size_bytes: 字节数

    Returns:
        str: 格式化的大小字符串（如 '1.5 MB'）
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# =============================================================================
# 批处理辅助函数
# Batch Processing Helper Functions
# =============================================================================


def batch_process(
    items: Sequence[Any],
    process_func: callable,
    *,
    on_error: str = "continue",
    progress_callback: Optional[callable] = None,
) -> tuple[list[Any], list[dict[str, Any]]]:
    """
    批量处理项目

    Args:
        items: 要处理的项目列表
        process_func: 处理函数，接收单个项目作为参数
        on_error: 错误处理策略 ('continue', 'stop', 'raise')
        progress_callback: 进度回调函数，接收 (current, total, item) 参数

    Returns:
        tuple: (成功结果列表, 错误列表)

    Example:
        >>> def process_image(path):
        ...     return ocr.predict(str(path))
        >>> results, errors = batch_process(images, process_image)
    """
    results = []
    errors = []
    total = len(items)

    for i, item in enumerate(items, 1):
        # 调用进度回调
        if progress_callback:
            progress_callback(i, total, item)

        try:
            result = process_func(item)
            results.append(result)
        except Exception as e:
            error_info = {
                "item": str(item),
                "error": str(e),
                "error_type": type(e).__name__,
            }
            errors.append(error_info)
            logger.warning(f"处理失败 [{i}/{total}]: {item} - {e}")

            if on_error == "stop":
                logger.error("遇到错误，停止处理")
                break
            elif on_error == "raise":
                raise

    return results, errors


def create_summary_report(
    total: int,
    success_count: int,
    errors: list[dict[str, Any]],
    *,
    extra_info: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    创建处理汇总报告

    Args:
        total: 总数
        success_count: 成功数
        errors: 错误列表
        extra_info: 额外信息

    Returns:
        dict: 汇总报告
    """
    report = {
        "summary": {
            "total": total,
            "success": success_count,
            "failed": len(errors),
            "success_rate": f"{(success_count / total * 100):.1f}%" if total > 0 else "N/A",
        },
        "timestamp": datetime.now().isoformat(),
        "errors": errors,
    }

    if extra_info:
        report["extra"] = extra_info

    return report


# =============================================================================
# 环境和系统函数
# Environment and System Functions
# =============================================================================


def get_env_or_default(key: str, default: str = "") -> str:
    """
    获取环境变量或返回默认值

    Args:
        key: 环境变量名
        default: 默认值

    Returns:
        str: 环境变量值或默认值
    """
    return os.environ.get(key, default)


def set_paddleocr_env() -> None:
    """
    设置 PaddleOCR 相关环境变量

    配置一些常用的环境变量以优化 PaddleOCR 的行为：
    - 禁用 OpenMP 警告
    - 设置线程数
    """
    # 解决 macOS 上的 OpenMP 库冲突问题
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

    # 减少不必要的日志输出
    os.environ.setdefault("GLOG_minloglevel", "2")


# =============================================================================
# 图片预处理函数（内存优化）
# Image Preprocessing Functions (Memory Optimization)
# =============================================================================


def resize_image_for_ocr(
    image_path: Union[str, Path],
    max_size: int = 1200,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    缩小大图片到适合 OCR 的尺寸（内存优化）

    在 macOS ARM 上，PaddleOCR 处理大图片时可能占用大量内存。
    建议在 OCR 之前先将大图片缩小到 1200-1600px，可显著降低内存占用，
    且对识别准确率影响极小。

    On macOS ARM, PaddleOCR may consume excessive memory when processing large images.
    It's recommended to resize large images to 1200-1600px before OCR, which significantly
    reduces memory usage with minimal impact on recognition accuracy.

    实测数据 (Benchmark):
    - 2000x3254 图片: 30GB 内存峰值 → 缩小后 5-7GB
    - 识别准确率: 几乎无影响 (95%+ 保持不变)

    Args:
        image_path: 输入图片路径
        max_size: 最大边长（默认 1200，推荐范围 1000-1600）
        output_path: 输出路径（默认保存到临时目录）

    Returns:
        处理后的图片路径

    Raises:
        OCRFileNotFoundError: 图片文件不存在
        OCROutputError: 图片保存失败

    Example:
        >>> from paddleocr import PaddleOCR
        >>> from examples._common import resize_image_for_ocr
        >>>
        >>> # 先缩小大图片
        >>> processed = resize_image_for_ocr("large_book_cover.png", max_size=1200)
        >>>
        >>> # 再进行 OCR 识别
        >>> ocr = PaddleOCR(
        ...     lang='ch',
        ...     use_doc_orientation_classify=False,
        ...     use_doc_unwarping=False,
        ...     use_textline_orientation=False,
        ... )
        >>> result = ocr.predict(processed)
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise OCROutputError(
            "Pillow 未安装，请运行: pip install Pillow",
            error_code="E501",
        ) from e

    # 验证输入文件
    path = Path(image_path)
    if not path.exists():
        raise OCRFileNotFoundError(
            f"图片文件不存在: {path}",
            file_path=str(path),
        )

    # 打开图片
    img = Image.open(path)
    original_size = (img.width, img.height)

    # 检查是否需要缩小
    max_dim = max(img.width, img.height)
    if max_dim <= max_size:
        logger.info(f"图片尺寸 {original_size} 无需缩小 (< {max_size}px)")
        return str(path)

    # 计算缩放比例
    scale = max_size / max_dim
    new_size = (int(img.width * scale), int(img.height * scale))

    logger.info(
        f"缩小图片: {original_size} → {new_size} (缩放比例: {scale:.2f})"
    )

    # 使用高质量重采样算法
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # 确定输出路径
    if output_path is None:
        # 使用临时目录
        import tempfile

        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / f"ocr_resized_{path.name}"
    else:
        output_path = Path(output_path)

    # 保存图片
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img_resized.save(output_path)
        logger.info(f"已保存缩小后的图片: {output_path}")
    except Exception as e:
        raise OCROutputError(
            f"保存图片失败: {e}",
            error_code="E502",
        ) from e

    return str(output_path)


# =============================================================================
# 初始化时设置环境
# Set environment on import
# =============================================================================

set_paddleocr_env()
