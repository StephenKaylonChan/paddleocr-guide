#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格识别示例 - 识别文档中的表格
Table Recognition Example - Recognize Tables in Documents

本示例演示了如何使用 PP-StructureV3 识别文档中的表格，
并将表格导出为多种格式（HTML、Markdown、CSV）。

PP-StructureV3 的表格识别功能支持：
- 有线表格和无线表格
- 复杂合并单元格
- 多表格检测
- 表格结构重建

This example demonstrates how to recognize tables in documents
using PP-StructureV3 and export them to various formats.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/document/02_table_recognition.py

依赖:
    pip install paddleocr
    pip install pandas  # 可选，用于 CSV 导出
"""

from __future__ import annotations

import gc
import sys
from dataclasses import dataclass, field
from io import StringIO
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
    OCROutputError,
    ensure_directory,
    get_logger,
    setup_logging,
)

# 配置模块日志器
logger = get_logger(__name__)

# 检测 pandas 是否可用
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class TableInfo:
    """
    单个表格的信息

    Attributes:
        index: 表格索引（从 0 开始）
        html: 表格的 HTML 表示
        row_count: 行数
        col_count: 列数
        bbox: 边界框坐标 [x1, y1, x2, y2]
    """

    index: int
    html: str = ""
    row_count: int = 0
    col_count: int = 0
    bbox: Optional[list[float]] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "index": self.index,
            "row_count": self.row_count,
            "col_count": self.col_count,
            "html_length": len(self.html),
            "bbox": self.bbox,
        }


@dataclass
class TableRecognitionResult:
    """
    表格识别结果

    Attributes:
        source_file: 源文件路径
        tables: 识别到的表格列表
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    tables: list[TableInfo] = field(default_factory=list)
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def table_count(self) -> int:
        """识别到的表格总数"""
        return len(self.tables)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "table_count": self.table_count,
            "page_count": self.page_count,
            "tables": [t.to_dict() for t in self.tables],
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 表格识别器类
# Table Recognizer Class
# =============================================================================


class TableRecognizer:
    """
    表格识别器 - 识别文档中的表格

    该类封装了 PP-StructureV3 的表格识别功能，支持：
    - 检测文档中的所有表格
    - 识别表格结构和内容
    - 导出为多种格式

    Attributes:
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> with TableRecognizer() as recognizer:
        ...     result = recognizer.recognize("table_image.png")
        ...     for table in result.tables:
        ...         print(f"表格 {table.index}: {table.row_count}行 x {table.col_count}列")
    """

    def __init__(
        self,
        *,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化表格识别器

        Args:
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "TableRecognizer":
        """初始化 PP-StructureV3 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化表格识别引擎...")

        try:
            from paddleocr import PPStructureV3

            # 仅启用表格识别，禁用其他功能以提高速度
            self._pipeline = PPStructureV3(
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
                use_table_recognition=True,
                use_formula_recognition=False,
                use_seal_recognition=False,
                use_chart_recognition=False,
            )
            self._initialized = True
            logger.info("表格识别引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"表格识别引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "TableRecognizer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        save_html: bool = True,
        save_csv: bool = False,
    ) -> TableRecognitionResult:
        """
        识别图片中的表格

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            save_html: 是否保存 HTML 格式
            save_csv: 是否保存 CSV 格式（需要 pandas）

        Returns:
            TableRecognitionResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("表格识别引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在识别表格: {path.name}")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            tables = []
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
                        # 保存 Markdown（包含表格）
                        res.save_to_markdown(save_path=str(output_path))

                        # 保存 JSON
                        res.save_to_json(save_path=str(output_path))

                        # 保存可视化图片
                        res.save_to_img(save_path=str(output_path))

                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"识别完成，共 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return TableRecognitionResult(
                source_file=str(path),
                tables=tables,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"表格识别失败: {e}")
            return TableRecognitionResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# HTML 转 CSV 功能
# HTML to CSV Functionality
# =============================================================================


def html_to_csv(
    html_content: str,
    output_path: Union[str, Path],
) -> bool:
    """
    将表格 HTML 转换为 CSV

    使用 pandas 解析 HTML 表格并导出为 CSV 格式。

    Args:
        html_content: 表格的 HTML 代码
        output_path: 输出 CSV 路径

    Returns:
        bool: 是否成功

    Note:
        需要安装 pandas: pip install pandas
    """
    if not PANDAS_AVAILABLE:
        logger.warning("pandas 未安装，无法导出 CSV")
        logger.info("请运行: pip install pandas")
        return False

    try:
        # 使用 pandas 解析 HTML 表格
        dfs = pd.read_html(StringIO(html_content))

        if not dfs:
            logger.warning("HTML 中未找到表格")
            return False

        # 保存第一个表格
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        dfs[0].to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"CSV 已保存: {output_file}")
        return True

    except Exception as e:
        logger.error(f"HTML 转 CSV 失败: {e}")
        return False


def html_to_excel(
    html_content: str,
    output_path: Union[str, Path],
) -> bool:
    """
    将表格 HTML 转换为 Excel

    使用 pandas 解析 HTML 表格并导出为 Excel 格式。

    Args:
        html_content: 表格的 HTML 代码
        output_path: 输出 Excel 路径

    Returns:
        bool: 是否成功

    Note:
        需要安装 pandas 和 openpyxl:
        pip install pandas openpyxl
    """
    if not PANDAS_AVAILABLE:
        logger.warning("pandas 未安装，无法导出 Excel")
        return False

    try:
        # 使用 pandas 解析 HTML 表格
        dfs = pd.read_html(StringIO(html_content))

        if not dfs:
            logger.warning("HTML 中未找到表格")
            return False

        # 保存第一个表格
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        dfs[0].to_excel(output_file, index=False, engine="openpyxl")
        logger.info(f"Excel 已保存: {output_file}")
        return True

    except ImportError:
        logger.warning("openpyxl 未安装，无法导出 Excel")
        logger.info("请运行: pip install openpyxl")
        return False
    except Exception as e:
        logger.error(f"HTML 转 Excel 失败: {e}")
        return False


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_tables(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> TableRecognitionResult:
    """
    便捷函数 - 识别图片中的表格

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        TableRecognitionResult: 识别结果

    Example:
        >>> result = recognize_tables("table.png", output_dir="./output")
        >>> print(f"识别到 {result.table_count} 个表格")
    """
    with TableRecognizer() as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示表格识别功能

    该函数展示了 PP-StructureV3 的表格识别功能：
    1. 识别文档中的表格
    2. 保存为多种格式
    3. 可选的 CSV/Excel 导出
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 50)
    logger.info("PP-StructureV3 表格识别示例")
    logger.info("=" * 50)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备包含表格的图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用表格识别器
        with TableRecognizer() as recognizer:
            result = recognizer.recognize(
                image_path,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 50)
                logger.info("处理完成!")
                logger.info(f"共处理 {result.page_count} 页")
            else:
                logger.error(f"处理失败: {result.error}")

        # 提示 CSV 导出功能
        if not PANDAS_AVAILABLE:
            logger.info("")
            logger.info("提示: 安装 pandas 可启用 CSV/Excel 导出功能")
            logger.info("运行: pip install pandas openpyxl")

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
