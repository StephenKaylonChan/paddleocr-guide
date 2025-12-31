#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 转 Markdown 示例 - 文档结构化转换
PDF to Markdown Example - Document Structured Conversion

本示例演示了如何使用 PP-StructureV3 将 PDF 或图片文档转换为 Markdown 格式。
PP-StructureV3 能够识别文档的版面结构（标题、段落、表格等），
并生成保持原有格式的 Markdown 文档。

This example demonstrates how to convert PDF or image documents to
Markdown format using PP-StructureV3. PP-StructureV3 can recognize
document layout structure and generate Markdown with preserved formatting.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/document/01_pdf_to_markdown.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import gc
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional, Union

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples._common import (  # 异常类; 上下文管理器; 日志; 配置; 工具函数
    PATH_CONFIG,
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    OCROutputError,
    StructureContextManager,
    ensure_directory,
    get_logger,
    is_supported_input,
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
class ConversionResult:
    """
    文档转换结果

    Attributes:
        source_file: 源文件路径
        markdown_content: 转换后的 Markdown 内容
        page_count: 页数（PDF 文档）
        output_files: 输出的文件列表
        success: 是否成功
        error: 错误信息（如果有）
    """

    source_file: str
    markdown_content: str = ""
    page_count: int = 0
    output_files: list[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    @property
    def preview(self) -> str:
        """获取 Markdown 内容预览（前 500 字符）"""
        if len(self.markdown_content) > 500:
            return self.markdown_content[:500] + "..."
        return self.markdown_content

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "markdown_length": len(self.markdown_content),
            "page_count": self.page_count,
            "output_files": self.output_files,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 文档转换器类
# Document Converter Class
# =============================================================================


class DocumentConverter:
    """
    文档转换器 - 将 PDF/图片转换为 Markdown

    该类封装了 PP-StructureV3 的文档转换功能，支持：
    - PDF 文档转换（多页支持）
    - 图片文档转换
    - 保留表格结构
    - 保留公式（可选）

    使用上下文管理器协议，确保资源正确释放。

    Attributes:
        use_table_recognition: 是否启用表格识别
        use_formula_recognition: 是否启用公式识别
        use_doc_orientation_classify: 是否启用文档方向分类

    Example:
        >>> with DocumentConverter() as converter:
        ...     result = converter.convert("document.pdf", output_dir="./output")
        ...     print(result.markdown_content)

        >>> # 或者使用便捷方法
        >>> markdown = convert_to_markdown("document.pdf")
    """

    def __init__(
        self,
        *,
        use_table_recognition: bool = True,
        use_formula_recognition: bool = False,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化文档转换器

        Args:
            use_table_recognition: 是否启用表格识别，默认 True
            use_formula_recognition: 是否启用公式识别，默认 False
                - 启用后可识别数学公式并转换为 LaTeX
                - 会增加处理时间
            use_doc_orientation_classify: 是否启用文档方向分类，默认 False
                - 启用后可自动检测并旋转倒置的文档
            use_doc_unwarping: 是否启用文档弯曲矫正，默认 False
                - 启用后可矫正弯曲/翘起的文档
        """
        self.use_table_recognition = use_table_recognition
        self.use_formula_recognition = use_formula_recognition
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

        logger.debug(
            f"DocumentConverter 配置: "
            f"table={use_table_recognition}, formula={use_formula_recognition}"
        )

    def initialize(self) -> "DocumentConverter":
        """
        初始化 PP-StructureV3 引擎

        Returns:
            DocumentConverter: 返回自身，支持链式调用

        Raises:
            OCRInitError: 初始化失败时
        """
        if self._initialized:
            return self

        logger.info("正在初始化 PP-StructureV3...")

        try:
            from paddleocr import PPStructureV3

            self._pipeline = PPStructureV3(
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
                use_table_recognition=self.use_table_recognition,
                use_formula_recognition=self.use_formula_recognition,
            )
            self._initialized = True
            logger.info("PP-StructureV3 初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"PP-StructureV3 初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            logger.debug("正在清理 PP-StructureV3 资源...")
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()
            logger.debug("PP-StructureV3 资源清理完成")

    def __enter__(self) -> "DocumentConverter":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def convert(
        self,
        input_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        save_json: bool = True,
        save_img: bool = False,
    ) -> ConversionResult:
        """
        转换文档为 Markdown

        将 PDF 或图片文档转换为 Markdown 格式，可选择保存到文件。

        Args:
            input_path: 输入文件路径（支持 PDF、PNG、JPG 等）
            output_dir: 输出目录，如果提供则保存结果文件
            save_json: 是否同时保存 JSON 格式结果
            save_img: 是否保存可视化结果图片

        Returns:
            ConversionResult: 转换结果对象

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("PP-StructureV3 未初始化，请先调用 initialize()")

        # 验证输入文件
        path = Path(input_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在转换文档: {path.name}")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            # 收集结果
            markdown_list = []
            page_count = 0
            output_files = []

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 获取 Markdown 内容
                if hasattr(res, "markdown"):
                    markdown_list.append(res.markdown)

                # 保存结果
                if output_dir:
                    try:
                        # 保存 Markdown
                        res.save_to_markdown(save_path=str(output_path))

                        # 保存 JSON
                        if save_json:
                            res.save_to_json(save_path=str(output_path))

                        # 保存可视化图片
                        if save_img:
                            res.save_to_img(save_path=str(output_path))

                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            # 合并多页 Markdown
            if len(markdown_list) > 1 and hasattr(self._pipeline, "concatenate_markdown_pages"):
                markdown_content = self._pipeline.concatenate_markdown_pages(markdown_list)
            elif markdown_list:
                markdown_content = "\n\n---\n\n".join(markdown_list)
            else:
                markdown_content = ""

            logger.info(f"转换完成，共 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return ConversionResult(
                source_file=str(path),
                markdown_content=markdown_content,
                page_count=page_count,
                output_files=output_files,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"转换失败: {e}")
            return ConversionResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def convert_to_markdown(
    input_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
    use_table: bool = True,
    use_formula: bool = False,
) -> str:
    """
    便捷函数 - 将文档转换为 Markdown

    这是最简单的使用方式，一行代码完成转换。

    Args:
        input_path: 输入文件路径
        output_dir: 输出目录（可选）
        use_table: 是否识别表格
        use_formula: 是否识别公式

    Returns:
        str: Markdown 内容

    Example:
        >>> markdown = convert_to_markdown("document.pdf")
        >>> print(markdown)

        >>> # 同时保存到文件
        >>> markdown = convert_to_markdown("document.pdf", output_dir="./output")
    """
    with DocumentConverter(
        use_table_recognition=use_table,
        use_formula_recognition=use_formula,
    ) as converter:
        result = converter.convert(input_path, output_dir=output_dir)

        if not result.success:
            logger.error(f"转换失败: {result.error}")
            return ""

        return result.markdown_content


def quick_convert(input_path: Union[str, Path], output_dir: Union[str, Path]) -> None:
    """
    快速转换并保存

    将文档转换为 Markdown 并保存到指定目录，
    同时打印处理结果。

    Args:
        input_path: 输入文件路径
        output_dir: 输出目录

    Example:
        >>> quick_convert("document.pdf", "./output")
    """
    logger.info(f"快速转换: {input_path}")

    with DocumentConverter() as converter:
        result = converter.convert(
            input_path,
            output_dir=output_dir,
            save_json=True,
            save_img=False,
        )

        if result.success:
            logger.info(f"转换完成，共 {result.page_count} 页")
            logger.info(f"Markdown 长度: {len(result.markdown_content)} 字符")
        else:
            logger.error(f"转换失败: {result.error}")


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示文档转 Markdown 功能

    该函数展示了 PP-StructureV3 的文档转换功能：
    1. 快速转换（保存文件）
    2. 获取 Markdown 内容
    3. 预览转换结果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 50)
    logger.info("PP-StructureV3 文档转换示例")
    logger.info("=" * 50)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试文档不存在: {image_path}")
        logger.info("请准备以下文件之一进行测试:")
        logger.info(f"  - {PATH_CONFIG.test_images_dir}/test.png (图片)")
        logger.info(f"  - {PATH_CONFIG.test_images_dir}/document.pdf (PDF)")
        return

    try:
        logger.info(f"处理文档: {image_path.name}")
        logger.info("")

        # 方法 1: 使用便捷函数快速转换
        logger.info("【方法 1】快速转换")
        logger.info("-" * 30)
        quick_convert(image_path, output_dir)

        # 方法 2: 使用 DocumentConverter 类
        logger.info("")
        logger.info("【方法 2】使用 DocumentConverter 类")
        logger.info("-" * 30)

        with DocumentConverter(
            use_table_recognition=True,
            use_formula_recognition=False,
        ) as converter:
            result = converter.convert(image_path)

            if result.success:
                logger.info(f"转换成功，共 {result.page_count} 页")
                logger.info("")
                logger.info("--- Markdown 预览 ---")
                logger.info(result.preview)
            else:
                logger.error(f"转换失败: {result.error}")

        logger.info("")
        logger.info("=" * 50)
        logger.info("转换完成!")

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
