#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公式识别示例 - 识别文档中的数学公式
Mathematical Formula Recognition Example

本示例演示了如何使用 PP-StructureV3 识别文档中的数学公式，
并将其转换为 LaTeX 格式。公式识别功能支持各种数学符号和结构。

常见应用场景：
- 学术论文公式提取
- 教材公式数字化
- 试卷公式识别
- 手写公式转换

This example demonstrates how to recognize mathematical formulas
in documents using PP-StructureV3 and convert them to LaTeX format.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/02_formula_recognition.py

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
class FormulaInfo:
    """
    单个公式的信息

    Attributes:
        index: 公式索引（从 0 开始）
        latex: 公式的 LaTeX 表示
        bbox: 边界框坐标 [x1, y1, x2, y2]
        confidence: 识别置信度
        is_inline: 是否为行内公式
    """

    index: int
    latex: str = ""
    bbox: Optional[list[float]] = None
    confidence: float = 0.0
    is_inline: bool = False

    @property
    def display_latex(self) -> str:
        """获取显示用的 LaTeX（带定界符）"""
        if self.is_inline:
            return f"${self.latex}$"
        return f"$${self.latex}$$"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "index": self.index,
            "latex": self.latex,
            "display_latex": self.display_latex,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "is_inline": self.is_inline,
        }


@dataclass
class FormulaRecognitionResult:
    """
    公式识别结果

    Attributes:
        source_file: 源文件路径
        formulas: 识别到的公式列表
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    formulas: list[FormulaInfo] = field(default_factory=list)
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def formula_count(self) -> int:
        """识别到的公式总数"""
        return len(self.formulas)

    @property
    def all_latex(self) -> list[str]:
        """所有公式的 LaTeX 列表"""
        return [f.latex for f in self.formulas]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "formula_count": self.formula_count,
            "page_count": self.page_count,
            "formulas": [f.to_dict() for f in self.formulas],
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 公式识别器类
# Formula Recognizer Class
# =============================================================================


class FormulaRecognizer:
    """
    公式识别器 - 识别文档中的数学公式

    该类封装了 PP-StructureV3 的公式识别功能，支持：
    - 检测文档中的所有公式区域
    - 将公式转换为 LaTeX 格式
    - 支持行内公式和行间公式
    - 支持复杂的数学结构

    支持的公式类型：
    - 分数、根号、指数、下标
    - 求和、积分、极限
    - 矩阵、方程组
    - 希腊字母、数学符号

    Attributes:
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> with FormulaRecognizer() as recognizer:
        ...     result = recognizer.recognize("math_paper.png")
        ...     for formula in result.formulas:
        ...         print(f"LaTeX: {formula.latex}")
    """

    def __init__(
        self,
        *,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化公式识别器

        Args:
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "FormulaRecognizer":
        """初始化 PP-StructureV3 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化公式识别引擎...")

        try:
            from paddleocr import PPStructureV3

            # 仅启用公式识别，禁用其他功能以提高速度
            self._pipeline = PPStructureV3(
                use_formula_recognition=True,  # 启用公式识别
                use_table_recognition=False,  # 禁用表格识别
                use_seal_recognition=False,  # 禁用印章识别
                use_chart_recognition=False,  # 禁用图表识别
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
            )
            self._initialized = True
            logger.info("公式识别引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"公式识别引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "FormulaRecognizer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        save_markdown: bool = True,
        save_visualization: bool = True,
    ) -> FormulaRecognitionResult:
        """
        识别图片中的数学公式

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            save_markdown: 是否保存 Markdown 格式（包含 LaTeX）
            save_visualization: 是否保存可视化结果

        Returns:
            FormulaRecognitionResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("公式识别引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在识别公式: {path.name}")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            formulas: list[FormulaInfo] = []
            page_count = 0
            formula_index = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 打印结果
                res.print()

                # 从 JSON 结果中提取公式信息
                try:
                    res_json = res.json
                    if "formula_res_list" in res_json:
                        for formula_data in res_json["formula_res_list"]:
                            latex = formula_data.get("rec_formula", "")
                            bbox = formula_data.get("bbox", None)

                            formula_info = FormulaInfo(
                                index=formula_index,
                                latex=latex,
                                bbox=bbox,
                            )
                            formulas.append(formula_info)
                            formula_index += 1

                            # 显示公式预览（截取前 50 字符）
                            preview = latex[:50] + "..." if len(latex) > 50 else latex
                            logger.info(f"  公式 #{formula_index}: {preview}")
                except Exception as e:
                    logger.warning(f"解析公式结果时出错: {e}")

                # 保存结果
                if output_dir:
                    try:
                        # 保存 Markdown（公式以 LaTeX 格式保存）
                        if save_markdown:
                            res.save_to_markdown(save_path=str(output_path))

                        res.save_to_json(save_path=str(output_path))

                        if save_visualization:
                            res.save_to_img(save_path=str(output_path))

                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"识别完成，共发现 {len(formulas)} 个公式")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")
                logger.info("公式已转换为 LaTeX 格式保存在 Markdown 文件中")

            return FormulaRecognitionResult(
                source_file=str(path),
                formulas=formulas,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"公式识别失败: {e}")
            return FormulaRecognitionResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_formulas(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> FormulaRecognitionResult:
    """
    便捷函数 - 识别图片中的数学公式

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        FormulaRecognitionResult: 识别结果

    Example:
        >>> result = recognize_formulas("math_paper.png")
        >>> print(f"发现 {result.formula_count} 个公式")
        >>> for formula in result.formulas:
        ...     print(f"  LaTeX: {formula.latex}")
    """
    with FormulaRecognizer() as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


def extract_latex(image_path: Union[str, Path]) -> list[str]:
    """
    便捷函数 - 提取所有公式的 LaTeX

    Args:
        image_path: 图片路径

    Returns:
        list[str]: LaTeX 公式列表

    Example:
        >>> latex_list = extract_latex("math_paper.png")
        >>> for latex in latex_list:
        ...     print(f"$${latex}$$")
    """
    result = recognize_formulas(image_path)
    return result.all_latex


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示公式识别功能

    该函数展示了 PP-StructureV3 的公式识别功能：
    1. 检测文档中的公式区域
    2. 将公式转换为 LaTeX 格式
    3. 保存 Markdown 和可视化结果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-StructureV3 公式识别示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "formula"

    # 打印说明
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 包含数学公式的文档图片")
    logger.info("  - 常见场景：教材、论文、试卷")
    logger.info("")
    logger.info("支持的公式类型:")
    logger.info("  - 分数、根号、指数、下标")
    logger.info("  - 求和、积分、极限")
    logger.info("  - 矩阵、方程组")
    logger.info("  - 希腊字母、数学符号")
    logger.info("")
    logger.info("输出格式:")
    logger.info("  - Markdown 文件（公式转为 LaTeX）")
    logger.info("  - JSON 文件（详细结构信息）")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备包含数学公式的文档图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用公式识别器
        with FormulaRecognizer() as recognizer:
            result = recognizer.recognize(
                image_path,
                output_dir=output_dir,
                save_markdown=True,
                save_visualization=True,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("识别完成!")
                logger.info(f"共处理 {result.page_count} 页")
                logger.info(f"发现 {result.formula_count} 个公式")

                if result.formulas:
                    logger.info("")
                    logger.info("识别到的公式 (LaTeX):")
                    for formula in result.formulas[:5]:  # 只显示前 5 个
                        preview = (
                            formula.latex[:60] + "..." if len(formula.latex) > 60 else formula.latex
                        )
                        logger.info(f"  [{formula.index + 1}] {preview}")
                    if result.formula_count > 5:
                        logger.info(f"  ... 共 {result.formula_count} 个公式")
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
