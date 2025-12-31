#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础 OCR 示例 - 单张图片文字识别
Basic OCR Example - Single Image Text Recognition

本示例演示了 PaddleOCR 最基础的使用方式：识别单张图片中的文字。
适合初学者快速上手 PaddleOCR，了解基本的 API 使用方法。

This example demonstrates the most basic usage of PaddleOCR:
recognizing text in a single image. Suitable for beginners to
quickly get started with PaddleOCR.

适用模型: PP-OCRv5 (默认，~10MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/basic/01_simple_ocr.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Iterator, Optional, Union

# 将项目根目录添加到 Python 路径，以便导入公共模块
# Add project root to Python path for importing common module
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples._common import (  # 异常类; 上下文管理器; 日志; 配置; 工具函数
    PATH_CONFIG,
    SUPPORTED_LANGUAGES,
    OCRContextManager,
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
# 核心函数
# Core Functions
# =============================================================================


def simple_ocr(
    image_path: Union[str, Path],
    *,
    lang: str = "ch",
    use_doc_orientation_classify: bool = False,
    use_doc_unwarping: bool = False,
    use_textline_orientation: bool = False,
) -> Iterator[Any]:
    """
    执行基础 OCR 识别

    使用 PaddleOCR 3.x API 识别图片中的文字。该函数使用上下文管理器
    自动管理 OCR 引擎的生命周期，确保资源正确释放。

    Args:
        image_path: 图片文件路径，支持 PNG/JPG/BMP/TIFF/WebP 格式
        lang: 语言代码，默认 'ch'（中文，同时支持英文）
              常用语言代码:
              - 'ch': 中文（含英文）- 推荐
              - 'en': 纯英文
              - 'japan': 日文
              - 'korean': 韩文
        use_doc_orientation_classify: 是否启用文档方向分类
            - True: 自动检测并旋转倒置的文档
            - False: 不进行方向检测（默认，速度更快）
        use_doc_unwarping: 是否启用文档弯曲矫正
            - True: 矫正弯曲/翘起的文档
            - False: 不进行矫正（默认）
        use_textline_orientation: 是否启用文本行方向分类
            - True: 处理倾斜的文本行
            - False: 不处理（默认）

    Returns:
        Iterator[Any]: PaddleOCR 结果对象迭代器
            每个结果对象支持以下方法:
            - result.print(): 打印识别结果
            - result.json: 获取 JSON 格式结果
            - result.save_to_json(path): 保存为 JSON 文件
            - result.save_to_img(path): 保存可视化图片

    Raises:
        OCRFileNotFoundError: 当图片文件不存在时
        OCRInitError: 当 OCR 引擎初始化失败时
        OCRException: 其他 OCR 相关错误

    Example:
        >>> # 基础使用
        >>> result = simple_ocr("test.png")
        >>> for res in result:
        ...     res.print()

        >>> # 指定语言
        >>> result = simple_ocr("japanese.png", lang="japan")

        >>> # 处理倒置文档
        >>> result = simple_ocr("rotated.png", use_doc_orientation_classify=True)
    """
    # 验证文件存在
    path = Path(image_path)
    if not path.exists():
        logger.error(f"图片文件不存在: {path}")
        raise OCRFileNotFoundError(
            f"图片文件不存在: {path}",
            file_path=str(path),
        )

    if not path.is_file():
        logger.error(f"路径不是文件: {path}")
        raise OCRFileNotFoundError(
            f"路径不是文件: {path}",
            file_path=str(path),
        )

    logger.info(f"开始识别图片: {path.name}")
    logger.debug(f"完整路径: {path}")
    logger.debug(f"语言: {lang}, 文档方向分类: {use_doc_orientation_classify}")

    # 使用上下文管理器确保资源正确释放
    with OCRContextManager(
        lang=lang,
        use_doc_orientation_classify=use_doc_orientation_classify,
        use_doc_unwarping=use_doc_unwarping,
        use_textline_orientation=use_textline_orientation,
    ) as ocr:
        # 执行识别
        result = ocr.predict(str(path))
        logger.info("识别完成")
        return result


def format_result(result: Any) -> None:
    """
    格式化输出识别结果

    使用 PaddleOCR 内置的 print() 方法输出识别结果。
    该方法会显示所有检测到的文本及其位置和置信度。

    Args:
        result: PaddleOCR 返回的结果对象迭代器

    Example:
        >>> result = simple_ocr("test.png")
        >>> format_result(result)
        # 输出类似:
        # rec_texts: ['你好', '世界']
        # rec_scores: [0.98, 0.95]
    """
    logger.info("=" * 50)
    logger.info("识别结果")
    logger.info("=" * 50)

    for res in result:
        # 使用 PaddleOCR 内置的 print 方法
        res.print()


def save_result_json(result: Any, output_dir: Union[str, Path]) -> Path:
    """
    保存识别结果为 JSON 文件

    将 OCR 识别结果保存为结构化的 JSON 文件，
    便于后续程序处理或数据分析。

    Args:
        result: PaddleOCR 返回的结果对象迭代器
        output_dir: 输出目录路径

    Returns:
        Path: JSON 文件保存路径

    Raises:
        OCRException: 保存失败时

    Example:
        >>> result = simple_ocr("test.png")
        >>> json_path = save_result_json(result, "./outputs")
        >>> print(f"已保存到: {json_path}")
    """
    output_path = ensure_directory(output_dir)

    for res in result:
        res.save_to_json(str(output_path))

    logger.info(f"JSON 结果已保存到: {output_path}")
    return output_path


def save_result_img(result: Any, output_dir: Union[str, Path]) -> Path:
    """
    保存可视化结果图片

    生成带有文本检测框和识别结果的可视化图片，
    便于直观查看识别效果。

    Args:
        result: PaddleOCR 返回的结果对象迭代器
        output_dir: 输出目录路径

    Returns:
        Path: 可视化图片保存路径

    Example:
        >>> result = simple_ocr("test.png")
        >>> img_path = save_result_img(result, "./outputs")
    """
    output_path = ensure_directory(output_dir)

    for res in result:
        res.save_to_img(str(output_path))

    logger.info(f"可视化图片已保存到: {output_path}")
    return output_path


def get_text_list(
    result: Any,
    *,
    min_confidence: float = 0.0,
) -> list[dict[str, Any]]:
    """
    从结果中提取文本列表

    将 PaddleOCR 的原始结果转换为易于使用的字典列表，
    每个字典包含文本内容和置信度。

    Args:
        result: PaddleOCR 返回的结果对象迭代器
        min_confidence: 最低置信度阈值（0.0-1.0），低于此值的结果将被过滤

    Returns:
        list[dict]: 文本列表，每项包含:
            - text: str - 识别的文本
            - confidence: float - 置信度 (0.0-1.0)

    Example:
        >>> result = simple_ocr("test.png")
        >>> texts = get_text_list(result, min_confidence=0.8)
        >>> for item in texts:
        ...     print(f"{item['text']} ({item['confidence']:.2%})")
    """
    return format_ocr_result(result, min_confidence=min_confidence)


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示基础 OCR 识别流程

    该函数展示了完整的 OCR 识别流程：
    1. 配置日志系统
    2. 检查测试图片是否存在
    3. 执行 OCR 识别
    4. 输出识别结果
    5. 可选：保存结果到文件
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 50)
    logger.info("PaddleOCR 基础 OCR 示例")
    logger.info("=" * 50)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir

    # 检查测试图片
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请将测试图片放入以下目录:")
        logger.info(f"  {PATH_CONFIG.test_images_dir}")
        logger.info("支持的格式: PNG, JPG, JPEG, BMP, TIFF, WebP")
        return

    try:
        # 执行 OCR 识别
        logger.info(f"正在识别: {image_path.name}")
        result = simple_ocr(image_path)

        # 输出结果
        format_result(result)

        # 可选：保存结果到文件
        # 取消注释以下代码以启用保存功能
        #
        # logger.info("保存结果...")
        # result = simple_ocr(image_path)  # 重新识别（迭代器只能遍历一次）
        # save_result_json(result, output_dir)
        #
        # result = simple_ocr(image_path)
        # save_result_img(result, output_dir)

        logger.info("识别完成!")

    except OCRFileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        raise SystemExit(1) from e

    except OCRInitError as e:
        logger.error(f"初始化错误: {e}")
        logger.error("请检查 PaddleOCR 是否正确安装:")
        logger.error("  pip install paddleocr")
        raise SystemExit(1) from e

    except OCRException as e:
        logger.error(f"OCR 错误: {e}")
        raise SystemExit(1) from e

    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
