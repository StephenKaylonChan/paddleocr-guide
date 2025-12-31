#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表识别示例 - 识别文档中的图表并提取数据
Chart Recognition Example - Recognize Charts and Extract Data

本示例演示了如何使用 PP-StructureV3 识别文档中的图表，
并将图表数据转换为结构化格式（表格）。

支持的图表类型：
- 柱状图（Bar Chart）
- 折线图（Line Chart）
- 饼图（Pie Chart）
- 散点图（Scatter Plot）
- 面积图（Area Chart）

This example demonstrates how to recognize charts in documents
using PP-StructureV3 and convert chart data to structured format.

适用模型: PP-StructureV3 (~50MB)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/03_chart_recognition.py

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
# 图表类型常量
# Chart Type Constants
# =============================================================================


class ChartType:
    """图表类型常量"""

    BAR = "bar"  # 柱状图
    LINE = "line"  # 折线图
    PIE = "pie"  # 饼图
    SCATTER = "scatter"  # 散点图
    AREA = "area"  # 面积图
    UNKNOWN = "unknown"  # 未知类型

    # 中文名称映射
    NAMES = {
        BAR: "柱状图",
        LINE: "折线图",
        PIE: "饼图",
        SCATTER: "散点图",
        AREA: "面积图",
        UNKNOWN: "未知类型",
    }

    @classmethod
    def get_name(cls, chart_type: str) -> str:
        """获取图表类型的中文名称"""
        return cls.NAMES.get(chart_type, chart_type)


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class ChartInfo:
    """
    单个图表的信息

    Attributes:
        index: 图表索引（从 0 开始）
        chart_type: 图表类型
        data: 图表数据（字典格式）
        title: 图表标题
        bbox: 边界框坐标 [x1, y1, x2, y2]
        confidence: 检测置信度
    """

    index: int
    chart_type: str = ChartType.UNKNOWN
    data: dict[str, Any] = field(default_factory=dict)
    title: str = ""
    bbox: Optional[list[float]] = None
    confidence: float = 0.0

    @property
    def type_name(self) -> str:
        """获取图表类型的中文名称"""
        return ChartType.get_name(self.chart_type)

    @property
    def has_data(self) -> bool:
        """是否有提取到的数据"""
        return bool(self.data)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "index": self.index,
            "chart_type": self.chart_type,
            "type_name": self.type_name,
            "title": self.title,
            "data": self.data,
            "has_data": self.has_data,
            "bbox": self.bbox,
            "confidence": self.confidence,
        }


@dataclass
class ChartRecognitionResult:
    """
    图表识别结果

    Attributes:
        source_file: 源文件路径
        charts: 识别到的图表列表
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    charts: list[ChartInfo] = field(default_factory=list)
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def chart_count(self) -> int:
        """识别到的图表总数"""
        return len(self.charts)

    def get_charts_by_type(self, chart_type: str) -> list[ChartInfo]:
        """获取指定类型的所有图表"""
        return [c for c in self.charts if c.chart_type == chart_type]

    def get_statistics(self) -> dict[str, int]:
        """获取各类型图表的统计信息"""
        stats: dict[str, int] = {}
        for chart in self.charts:
            stats[chart.chart_type] = stats.get(chart.chart_type, 0) + 1
        return stats

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "chart_count": self.chart_count,
            "page_count": self.page_count,
            "statistics": self.get_statistics(),
            "charts": [c.to_dict() for c in self.charts],
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 图表识别器类
# Chart Recognizer Class
# =============================================================================


class ChartRecognizer:
    """
    图表识别器 - 识别文档中的图表

    该类封装了 PP-StructureV3 的图表识别功能，支持：
    - 检测文档中的所有图表
    - 识别图表类型（柱状图、折线图、饼图等）
    - 提取图表数据并转换为结构化格式
    - 支持同时识别表格（图表数据可能输出为表格）

    Attributes:
        use_table_recognition: 是否同时启用表格识别
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> with ChartRecognizer() as recognizer:
        ...     result = recognizer.recognize("report.png")
        ...     for chart in result.charts:
        ...         print(f"图表类型: {chart.type_name}")
        ...         print(f"数据: {chart.data}")
    """

    def __init__(
        self,
        *,
        use_table_recognition: bool = True,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化图表识别器

        Args:
            use_table_recognition: 是否同时启用表格识别（图表数据可能输出为表格）
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_table_recognition = use_table_recognition
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "ChartRecognizer":
        """初始化 PP-StructureV3 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化图表识别引擎...")

        try:
            from paddleocr import PPStructureV3

            self._pipeline = PPStructureV3(
                use_chart_recognition=True,  # 启用图表识别
                use_table_recognition=self.use_table_recognition,
                use_formula_recognition=False,  # 禁用公式识别
                use_seal_recognition=False,  # 禁用印章识别
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
            )
            self._initialized = True
            logger.info("图表识别引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"图表识别引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "ChartRecognizer":
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
    ) -> ChartRecognitionResult:
        """
        识别图片中的图表

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）
            save_markdown: 是否保存 Markdown 格式
            save_visualization: 是否保存可视化结果

        Returns:
            ChartRecognitionResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("图表识别引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在识别图表: {path.name}")

        try:
            # 执行预测
            output = self._pipeline.predict(input=str(path))

            charts: list[ChartInfo] = []
            page_count = 0
            chart_index = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 打印结果
                res.print()

                # 从 JSON 结果中提取图表信息
                try:
                    res_json = res.json
                    if "chart_res_list" in res_json:
                        for chart_data in res_json["chart_res_list"]:
                            chart_type = chart_data.get("chart_type", ChartType.UNKNOWN)
                            data = chart_data.get("chart_data", {})
                            title = chart_data.get("title", "")
                            bbox = chart_data.get("bbox", None)

                            chart_info = ChartInfo(
                                index=chart_index,
                                chart_type=chart_type,
                                data=data,
                                title=title,
                                bbox=bbox,
                            )
                            charts.append(chart_info)
                            chart_index += 1

                            logger.info(f"  图表 #{chart_index}: {chart_info.type_name}")
                            if chart_info.title:
                                logger.info(f"    标题: {chart_info.title}")
                except Exception as e:
                    logger.warning(f"解析图表结果时出错: {e}")

                # 保存结果
                if output_dir:
                    try:
                        if save_markdown:
                            res.save_to_markdown(save_path=str(output_path))

                        res.save_to_json(save_path=str(output_path))

                        if save_visualization:
                            res.save_to_img(save_path=str(output_path))

                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"识别完成，共发现 {len(charts)} 个图表")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")
                logger.info("图表数据已转换为表格格式保存在 Markdown 文件中")

            return ChartRecognitionResult(
                source_file=str(path),
                charts=charts,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"图表识别失败: {e}")
            return ChartRecognitionResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_charts(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> ChartRecognitionResult:
    """
    便捷函数 - 识别图片中的图表

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        ChartRecognitionResult: 识别结果

    Example:
        >>> result = recognize_charts("report.png")
        >>> print(f"发现 {result.chart_count} 个图表")
        >>> for chart in result.charts:
        ...     print(f"  类型: {chart.type_name}")
    """
    with ChartRecognizer() as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


def extract_chart_data(image_path: Union[str, Path]) -> list[dict[str, Any]]:
    """
    便捷函数 - 提取所有图表数据

    Args:
        image_path: 图片路径

    Returns:
        list[dict]: 图表数据列表

    Example:
        >>> data_list = extract_chart_data("report.png")
        >>> for data in data_list:
        ...     print(data)
    """
    result = recognize_charts(image_path)
    return [{"type": c.chart_type, "title": c.title, "data": c.data} for c in result.charts]


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示图表识别功能

    该函数展示了 PP-StructureV3 的图表识别功能：
    1. 检测文档中的图表区域
    2. 识别图表类型
    3. 提取图表数据
    4. 保存结构化结果
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-StructureV3 图表识别示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "chart"

    # 打印说明
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 包含图表的文档图片")
    logger.info("  - 常见场景：报告、论文、PPT截图")
    logger.info("")
    logger.info("支持的图表类型:")
    logger.info("  - 柱状图（Bar Chart）")
    logger.info("  - 折线图（Line Chart）")
    logger.info("  - 饼图（Pie Chart）")
    logger.info("  - 散点图（Scatter Plot）")
    logger.info("  - 面积图（Area Chart）")
    logger.info("")
    logger.info("输出格式:")
    logger.info("  - 图表数据转换为表格")
    logger.info("  - Markdown 和 JSON 格式保存")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备包含图表的文档图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用图表识别器
        with ChartRecognizer() as recognizer:
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
                logger.info(f"发现 {result.chart_count} 个图表")

                # 显示统计信息
                stats = result.get_statistics()
                if stats:
                    logger.info("")
                    logger.info("图表类型统计:")
                    for chart_type, count in stats.items():
                        type_name = ChartType.get_name(chart_type)
                        logger.info(f"  {type_name}: {count} 个")

                # 显示图表详情
                if result.charts:
                    logger.info("")
                    logger.info("图表详情:")
                    for chart in result.charts:
                        logger.info(f"  [{chart.index + 1}] {chart.type_name}")
                        if chart.title:
                            logger.info(f"      标题: {chart.title}")
                        if chart.has_data:
                            logger.info(f"      数据: 已提取")
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
