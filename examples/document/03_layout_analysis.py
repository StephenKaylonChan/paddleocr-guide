#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版面分析示例 - 分析文档结构
Layout Analysis Example - Analyze Document Structure

本示例演示了如何使用 PP-StructureV3 分析文档的版面结构。
版面分析可以识别文档中的不同区域类型，包括：
- 标题（title）
- 正文（text）
- 表格（table）
- 图片（figure）
- 列表（list）
- 公式（equation）
- 页眉/页脚（header/footer）

This example demonstrates how to analyze document layout structure
using PP-StructureV3. Layout analysis can identify different region
types including titles, text, tables, figures, lists, equations, etc.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/document/03_layout_analysis.py

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
# 版面区域类型常量
# Layout Region Type Constants
# =============================================================================


class LayoutType:
    """版面区域类型常量"""

    TITLE = "title"  # 标题
    TEXT = "text"  # 正文
    TABLE = "table"  # 表格
    FIGURE = "figure"  # 图片
    LIST = "list"  # 列表
    EQUATION = "equation"  # 公式
    HEADER = "header"  # 页眉
    FOOTER = "footer"  # 页脚
    REFERENCE = "reference"  # 参考文献
    ABSTRACT = "abstract"  # 摘要

    # 所有类型
    ALL = {TITLE, TEXT, TABLE, FIGURE, LIST, EQUATION, HEADER, FOOTER, REFERENCE, ABSTRACT}


# 类型名称中文映射
LAYOUT_TYPE_NAMES = {
    LayoutType.TITLE: "标题",
    LayoutType.TEXT: "正文",
    LayoutType.TABLE: "表格",
    LayoutType.FIGURE: "图片",
    LayoutType.LIST: "列表",
    LayoutType.EQUATION: "公式",
    LayoutType.HEADER: "页眉",
    LayoutType.FOOTER: "页脚",
    LayoutType.REFERENCE: "参考文献",
    LayoutType.ABSTRACT: "摘要",
}


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class LayoutRegion:
    """
    版面区域信息

    Attributes:
        region_type: 区域类型（title, text, table 等）
        bbox: 边界框坐标 [x1, y1, x2, y2]
        content: 区域内容（如文本）
        confidence: 检测置信度
        order: 阅读顺序
    """

    region_type: str
    bbox: list[float] = field(default_factory=list)
    content: str = ""
    confidence: float = 0.0
    order: int = 0

    @property
    def type_name(self) -> str:
        """获取类型的中文名称"""
        return LAYOUT_TYPE_NAMES.get(self.region_type, self.region_type)

    @property
    def area(self) -> float:
        """计算区域面积"""
        if len(self.bbox) >= 4:
            width = self.bbox[2] - self.bbox[0]
            height = self.bbox[3] - self.bbox[1]
            return width * height
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.region_type,
            "type_name": self.type_name,
            "bbox": self.bbox,
            "content_preview": self.content[:100] if self.content else "",
            "confidence": self.confidence,
            "order": self.order,
        }


@dataclass
class LayoutAnalysisResult:
    """
    版面分析结果

    Attributes:
        source_file: 源文件路径
        regions: 识别到的版面区域列表
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    regions: list[LayoutRegion] = field(default_factory=list)
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def region_count(self) -> int:
        """区域总数"""
        return len(self.regions)

    def get_regions_by_type(self, region_type: str) -> list[LayoutRegion]:
        """获取指定类型的所有区域"""
        return [r for r in self.regions if r.region_type == region_type]

    def get_statistics(self) -> dict[str, int]:
        """获取各类型区域的统计信息"""
        stats = {}
        for region in self.regions:
            stats[region.region_type] = stats.get(region.region_type, 0) + 1
        return stats

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "region_count": self.region_count,
            "page_count": self.page_count,
            "statistics": self.get_statistics(),
            "regions": [r.to_dict() for r in self.regions],
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 版面分析器类
# Layout Analyzer Class
# =============================================================================


class LayoutAnalyzer:
    """
    版面分析器 - 分析文档版面结构

    该类封装了 PP-StructureV3 的版面分析功能，可以识别：
    - 标题和正文
    - 表格和图片
    - 公式和列表
    - 页眉和页脚

    Attributes:
        use_table_recognition: 是否启用表格识别
        use_formula_recognition: 是否启用公式识别
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> with LayoutAnalyzer() as analyzer:
        ...     result = analyzer.analyze("document.png")
        ...     stats = result.get_statistics()
        ...     print(f"标题: {stats.get('title', 0)} 个")
        ...     print(f"正文: {stats.get('text', 0)} 个")
    """

    def __init__(
        self,
        *,
        use_table_recognition: bool = True,
        use_formula_recognition: bool = True,
        use_doc_orientation_classify: bool = True,
        use_doc_unwarping: bool = False,
        use_seal_recognition: bool = False,
        use_chart_recognition: bool = False,
    ) -> None:
        """
        初始化版面分析器

        Args:
            use_table_recognition: 是否启用表格识别
            use_formula_recognition: 是否启用公式识别
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
            use_seal_recognition: 是否启用印章识别
            use_chart_recognition: 是否启用图表识别
        """
        self.use_table_recognition = use_table_recognition
        self.use_formula_recognition = use_formula_recognition
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping
        self.use_seal_recognition = use_seal_recognition
        self.use_chart_recognition = use_chart_recognition

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "LayoutAnalyzer":
        """初始化 PP-StructureV3 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化版面分析引擎...")

        try:
            from paddleocr import PPStructureV3

            self._pipeline = PPStructureV3(
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
                use_table_recognition=self.use_table_recognition,
                use_formula_recognition=self.use_formula_recognition,
                use_seal_recognition=self.use_seal_recognition,
                use_chart_recognition=self.use_chart_recognition,
            )
            self._initialized = True
            logger.info("版面分析引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"版面分析引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "LayoutAnalyzer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def analyze(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
        save_visualization: bool = True,
    ) -> LayoutAnalysisResult:
        """
        分析文档版面结构

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            save_visualization: 是否保存可视化结果

        Returns:
            LayoutAnalysisResult: 分析结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("版面分析引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在分析版面: {path.name}")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            regions = []
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
                        # 保存 Markdown
                        res.save_to_markdown(save_path=str(output_path))

                        # 保存 JSON
                        res.save_to_json(save_path=str(output_path))

                        # 保存可视化图片
                        if save_visualization:
                            res.save_to_img(save_path=str(output_path))

                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"分析完成，共 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return LayoutAnalysisResult(
                source_file=str(path),
                regions=regions,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"版面分析失败: {e}")
            return LayoutAnalysisResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def analyze_layout(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> LayoutAnalysisResult:
    """
    便捷函数 - 分析文档版面

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        LayoutAnalysisResult: 分析结果

    Example:
        >>> result = analyze_layout("document.png", output_dir="./output")
        >>> print(f"识别到 {result.region_count} 个区域")
    """
    with LayoutAnalyzer() as analyzer:
        return analyzer.analyze(image_path, output_dir=output_dir)


def quick_analysis(image_path: Union[str, Path]) -> None:
    """
    快速版面分析（仅输出，不保存）

    Args:
        image_path: 图片路径

    Example:
        >>> quick_analysis("document.png")
    """
    logger.info(f"快速分析: {image_path}")

    with LayoutAnalyzer() as analyzer:
        result = analyzer.analyze(image_path)

        if result.success:
            logger.info(f"分析完成，共 {result.page_count} 页")
        else:
            logger.error(f"分析失败: {result.error}")


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示版面分析功能

    该函数展示了 PP-StructureV3 的版面分析功能：
    1. 检测文档中的各类区域
    2. 输出区域类型和位置
    3. 保存分析结果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-StructureV3 版面分析示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备文档图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"分析文档: {image_path.name}")
        logger.info("")

        # 使用版面分析器
        with LayoutAnalyzer(
            use_table_recognition=True,
            use_formula_recognition=True,
            use_doc_orientation_classify=True,
        ) as analyzer:
            result = analyzer.analyze(
                image_path,
                output_dir=output_dir,
                save_visualization=True,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("分析完成!")
                logger.info(f"共处理 {result.page_count} 页")
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
