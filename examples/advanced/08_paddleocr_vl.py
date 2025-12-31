#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉语言模型示例 - 使用 PaddleOCR-VL
Vision-Language Model Example - Using PaddleOCR-VL

本示例演示了如何使用 PaddleOCR-VL 进行复杂文档理解。
PaddleOCR-VL 是一个轻量级的视觉语言模型，支持多语言 OCR 和文档理解。

⚠️ 重要平台限制：
   PaddleOCR-VL 不支持 macOS ARM (M1/M2/M3/M4)
   仅支持: x86 架构 Linux/Windows / NVIDIA GPU (CUDA)

模型特点：
- 0.9B 参数，轻量级 VLM
- 支持 109 种语言
- 图表、公式、表格综合理解
- 手写与印刷混合识别

This example demonstrates how to use PaddleOCR-VL for complex
document understanding. Note that PaddleOCR-VL does NOT support
macOS ARM architecture.

适用模型: PaddleOCR-VL (0.9B 参数)
支持系统: x86 Linux / Windows / NVIDIA GPU（不支持 macOS ARM）
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/08_paddleocr_vl.py

依赖:
    pip install paddleocr
"""

from __future__ import annotations

import gc
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from examples._common import (  # 异常类; 日志; 配置; 工具函数
    PATH_CONFIG,
    PLATFORM_INFO,
    OCRException,
    OCRFileNotFoundError,
    OCRInitError,
    OCRPlatformError,
    ensure_directory,
    get_logger,
    setup_logging,
)

# 配置模块日志器
logger = get_logger(__name__)


# =============================================================================
# 平台兼容性检查
# Platform Compatibility Check
# =============================================================================


def check_vl_platform_compatibility() -> tuple[bool, str]:
    """
    检查 PaddleOCR-VL 的平台兼容性

    PaddleOCR-VL 不支持 macOS ARM 架构。

    Returns:
        tuple[bool, str]: (是否兼容, 平台信息)
    """
    machine = platform.machine().lower()
    system = platform.system().lower()

    if system == "darwin" and machine in ("arm64", "aarch64"):
        return False, "macOS ARM (M1/M2/M3/M4) - 不支持"
    elif machine in ("arm64", "aarch64"):
        return False, f"ARM64 ({system}) - 不支持"
    else:
        return True, f"{system} {machine} - 支持"


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class VLRecognitionResult:
    """
    视觉语言模型识别结果

    Attributes:
        source_file: 源文件路径
        markdown_content: Markdown 格式的识别结果
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    markdown_content: str = ""
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def preview(self) -> str:
        """获取内容预览（前 500 字符）"""
        if len(self.markdown_content) > 500:
            return self.markdown_content[:500] + "..."
        return self.markdown_content

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "markdown_length": len(self.markdown_content),
            "page_count": self.page_count,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 视觉语言模型识别器类
# Vision-Language Model Recognizer Class
# =============================================================================


class VLRecognizer:
    """
    视觉语言模型识别器 - 使用 PaddleOCR-VL

    该类封装了 PaddleOCR-VL 的文档识别功能，支持：
    - 109 种语言的多语言 OCR
    - 复杂文档结构理解
    - 图表、公式、表格综合识别
    - 手写与印刷混合识别

    ⚠️ 平台限制：
    - 不支持 macOS ARM (M1/M2/M3/M4)
    - 推荐使用 x86 Linux + NVIDIA GPU

    Attributes:
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> # 先检查平台兼容性
        >>> compatible, info = check_vl_platform_compatibility()
        >>> if compatible:
        ...     with VLRecognizer() as recognizer:
        ...         result = recognizer.recognize("complex_doc.png")
        ...         print(result.markdown_content)
    """

    def __init__(
        self,
        *,
        use_doc_orientation_classify: bool = True,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化视觉语言模型识别器

        Args:
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._vl: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "VLRecognizer":
        """初始化 PaddleOCR-VL 引擎"""
        if self._initialized:
            return self

        # 检查平台兼容性
        compatible, platform_info = check_vl_platform_compatibility()

        if not compatible:
            raise OCRPlatformError(
                f"PaddleOCR-VL 不支持当前平台: {platform_info}",
                error_code="E601",
                details={
                    "platform": platform_info,
                    "supported": ["x86_64 Linux", "x86_64 Windows", "NVIDIA GPU (CUDA)"],
                },
            )

        logger.info("正在初始化 PaddleOCR-VL 引擎...")
        logger.info(f"当前平台: {platform_info}")

        try:
            from paddleocr import PaddleOCRVL

            self._vl = PaddleOCRVL(
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
            )
            self._initialized = True
            logger.info("PaddleOCR-VL 引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装或 VL 模块不可用",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"PaddleOCR-VL 引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._vl is not None:
            del self._vl
            self._vl = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "VLRecognizer":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def recognize(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> VLRecognitionResult:
        """
        使用视觉语言模型识别文档

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）

        Returns:
            VLRecognitionResult: 识别结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("PaddleOCR-VL 引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在使用 VL 模型识别: {path.name}")

        try:
            # 执行预测
            output = self._vl.predict(str(path))

            markdown_content = ""
            page_count = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 打印结果
                res.print()

                # 获取 Markdown 内容
                if hasattr(res, "markdown"):
                    markdown_content += res.markdown

                # 保存结果
                if output_dir:
                    try:
                        res.save_to_markdown(save_path=str(output_path))
                        res.save_to_json(save_path=str(output_path))
                        res.save_to_img(save_path=str(output_path))
                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"识别完成，共处理 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return VLRecognitionResult(
                source_file=str(path),
                markdown_content=markdown_content,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"VL 模型识别失败: {e}")
            return VLRecognitionResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def recognize_with_vl(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> VLRecognitionResult:
    """
    便捷函数 - 使用视觉语言模型识别文档

    ⚠️ 注意：不支持 macOS ARM 架构

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        VLRecognitionResult: 识别结果

    Example:
        >>> result = recognize_with_vl("complex_doc.png")
        >>> print(result.markdown_content)
    """
    with VLRecognizer() as recognizer:
        return recognizer.recognize(image_path, output_dir=output_dir)


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示 PaddleOCR-VL 视觉语言模型

    该函数展示了 PaddleOCR-VL 的功能：
    1. 平台兼容性检查
    2. 多语言文档识别
    3. 复杂结构理解
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PaddleOCR-VL 视觉语言模型示例")
    logger.info("=" * 60)

    # 检查平台兼容性
    compatible, platform_info = check_vl_platform_compatibility()

    logger.info("")
    logger.info(f"当前平台: {platform_info}")
    logger.info("")

    if not compatible:
        logger.warning("⚠️  警告: PaddleOCR-VL 不支持当前平台!")
        logger.info("")
        logger.info("支持的平台:")
        logger.info("  - x86_64 Linux (推荐)")
        logger.info("  - x86_64 Windows")
        logger.info("  - NVIDIA GPU (CUDA)")
        logger.info("")
        logger.info("替代方案:")
        logger.info("  - 使用 PP-OCRv5 进行基础 OCR")
        logger.info("  - 使用 PP-StructureV3 进行文档解析")
        logger.info("  - 在支持的服务器上部署 VL 模型")
        logger.info("")
        logger.info("由于平台不兼容，示例无法运行。")
        return

    logger.info("✅ 平台兼容，可以运行 VL 模型")
    logger.info("")
    logger.info("模型特点:")
    logger.info("  - 0.9B 参数，轻量级 VLM")
    logger.info("  - 109 种语言支持")
    logger.info("  - 图表、公式、表格综合理解")
    logger.info("  - 手写与印刷混合识别")
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 复杂多语言文档")
    logger.info("  - 图表/公式/表格综合文档")
    logger.info("")

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "vl"

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备复杂文档图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用 VL 模型识别
        with VLRecognizer() as recognizer:
            result = recognizer.recognize(
                image_path,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("识别完成!")
                logger.info(f"共处理 {result.page_count} 页")
                logger.info(f"Markdown 长度: {len(result.markdown_content)} 字符")

                if result.markdown_content:
                    logger.info("")
                    logger.info("--- 内容预览 ---")
                    logger.info(result.preview)
            else:
                logger.error(f"识别失败: {result.error}")

    except OCRPlatformError as e:
        logger.error(f"平台错误: {e}")
        logger.info("")
        logger.info("请在支持的平台上运行此示例")
        raise SystemExit(1) from e

    except OCRFileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        raise SystemExit(1) from e

    except OCRInitError as e:
        logger.error(f"初始化错误: {e}")
        logger.info("")
        logger.info("可能原因:")
        logger.info("  - 模型文件未下载完成")
        logger.info("  - 内存不足（VL 模型需要较大内存）")
        logger.info("  - CUDA 环境问题")
        raise SystemExit(1) from e

    except OCRException as e:
        logger.error(f"OCR 错误: {e}")
        raise SystemExit(1) from e

    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
