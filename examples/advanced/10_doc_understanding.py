#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档理解示例 - 使用 DocUnderstanding
Document Understanding Example - Using DocUnderstanding

本示例演示了如何使用 DocUnderstanding 进行深度文档理解。
DocUnderstanding 可以理解文档内容并回答关于文档的问题。

⚠️ 重要平台限制：
   DocUnderstanding 基于 VLM，不支持 macOS ARM (M1/M2/M3/M4)
   仅支持: x86 架构 Linux/Windows / NVIDIA GPU (CUDA)

功能说明：
- 深度理解文档内容
- 回答关于文档的问题
- 提取关键信息
- 理解表格和图表

典型应用场景：
- 合同审查：「这份合同的有效期是多久？」
- 报告分析：「文档的主要结论是什么？」
- 表格理解：「表格中的最大值是多少？」

This example demonstrates how to use DocUnderstanding for deep
document understanding. Note that this feature is based on VLM
and does NOT support macOS ARM architecture.

适用模型: DocUnderstanding (基于 VLM)
支持系统: x86 Linux / Windows / NVIDIA GPU（不支持 macOS ARM）
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/10_doc_understanding.py

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


def check_doc_understanding_compatibility() -> tuple[bool, str]:
    """
    检查 DocUnderstanding 的平台兼容性

    DocUnderstanding 基于 VLM，不支持 macOS ARM 架构。

    Returns:
        tuple[bool, str]: (是否兼容, 平台信息)
    """
    machine = platform.machine().lower()
    system = platform.system().lower()

    if system == "darwin" and machine in ("arm64", "aarch64"):
        return False, "macOS ARM (M1/M2/M3/M4) - 不支持"
    elif machine in ("arm64", "aarch64"):
        return False, f"ARM64 ({system}) - 可能不支持"
    else:
        return True, f"{system} {machine} - 支持"


# =============================================================================
# 预设问题模板
# Predefined Question Templates
# =============================================================================


class QuestionTemplates:
    """预设的文档问题模板"""

    # 通用问题
    GENERAL = "这个文档的主题是什么？"
    KEY_INFO = "文档中提到了哪些关键信息？"
    DATE = "文档的日期是什么？"
    SUMMARY = "请总结这个文档的主要内容"

    # 合同相关
    CONTRACT_PARTIES = "合同的甲方和乙方分别是谁？"
    CONTRACT_AMOUNT = "合同金额是多少？"
    CONTRACT_PERIOD = "合同的有效期是多久？"

    # 报告相关
    REPORT_CONCLUSION = "报告的主要结论是什么？"
    REPORT_DATA = "报告中的关键数据是什么？"

    # 表格相关
    TABLE_MAX = "表格中的最大值是多少？"
    TABLE_TOTAL = "表格的合计是多少？"


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class QAResult:
    """
    问答结果

    Attributes:
        question: 问题
        answer: 答案
        confidence: 置信度
    """

    question: str
    answer: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "question": self.question,
            "answer": self.answer,
            "confidence": self.confidence,
        }


@dataclass
class UnderstandingResult:
    """
    文档理解结果

    Attributes:
        source_file: 源文件路径
        qa_results: 问答结果列表
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    qa_results: list[QAResult] = field(default_factory=list)
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def question_count(self) -> int:
        """问答数量"""
        return len(self.qa_results)

    def get_answer(self, question: str) -> Optional[str]:
        """获取指定问题的答案"""
        for qa in self.qa_results:
            if qa.question == question:
                return qa.answer
        return None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "question_count": self.question_count,
            "page_count": self.page_count,
            "qa_results": [qa.to_dict() for qa in self.qa_results],
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 文档理解器类
# Document Understanding Class
# =============================================================================


class DocumentUnderstanding:
    """
    文档理解器 - 深度理解文档内容

    该类封装了 DocUnderstanding 的文档理解功能，支持：
    - 深度理解文档内容
    - 回答关于文档的问题
    - 提取关键信息
    - 理解表格和图表

    ⚠️ 平台限制：
    - 不支持 macOS ARM (M1/M2/M3/M4)
    - 推荐使用 x86 Linux + NVIDIA GPU

    Attributes:
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> # 先检查平台兼容性
        >>> compatible, info = check_doc_understanding_compatibility()
        >>> if compatible:
        ...     with DocumentUnderstanding() as doc:
        ...         result = doc.understand("contract.png")
        ...         answer = doc.ask("contract.png", "合同金额是多少？")
    """

    def __init__(
        self,
        *,
        use_doc_orientation_classify: bool = True,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化文档理解器

        Args:
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._doc_understand: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "DocumentUnderstanding":
        """初始化 DocUnderstanding 引擎"""
        if self._initialized:
            return self

        # 检查平台兼容性
        compatible, platform_info = check_doc_understanding_compatibility()

        logger.info("正在初始化文档理解引擎...")
        logger.info(f"当前平台: {platform_info}")

        if not compatible:
            logger.warning("⚠️  当前平台可能不支持 VLM 模型")

        try:
            from paddleocr import DocUnderstanding as DocUnderstandingPipeline

            self._doc_understand = DocUnderstandingPipeline(
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
            )
            self._initialized = True
            logger.info("文档理解引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装或 DocUnderstanding 模块不可用",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"文档理解引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._doc_understand is not None:
            del self._doc_understand
            self._doc_understand = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "DocumentUnderstanding":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def understand(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> UnderstandingResult:
        """
        理解文档内容

        Args:
            image_path: 图片路径
            output_dir: 输出目录（可选）

        Returns:
            UnderstandingResult: 理解结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("文档理解引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"正在分析文档: {path.name}")

        try:
            # 执行文档理解
            output = self._doc_understand.predict(input=str(path))

            page_count = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1
                res.print()

                # 保存结果
                if output_dir:
                    try:
                        res.save_to_json(save_path=str(output_path))
                        res.save_to_markdown(save_path=str(output_path))
                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"文档分析完成，共处理 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return UnderstandingResult(
                source_file=str(path),
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"文档理解失败: {e}")
            return UnderstandingResult(
                source_file=str(path),
                success=False,
                error=str(e),
            )

    def ask(
        self,
        image_path: Union[str, Path],
        question: str,
    ) -> QAResult:
        """
        询问文档内容

        Args:
            image_path: 图片路径
            question: 问题

        Returns:
            QAResult: 问答结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("文档理解引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        logger.info(f"问题: {question}")

        try:
            # 带问题的预测
            output = self._doc_understand.predict(
                input=str(path),
                prompt=question,
            )

            answer = ""
            for res in output:
                try:
                    res_json = res.json
                    answer = res_json.get("answer", "")
                    break
                except Exception:
                    pass

            logger.info(f"答案: {answer if answer else '未找到答案'}")

            return QAResult(
                question=question,
                answer=answer,
            )

        except Exception as e:
            logger.error(f"问答失败: {e}")
            return QAResult(
                question=question,
                answer=f"错误: {e}",
            )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def understand_document(
    image_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
) -> UnderstandingResult:
    """
    便捷函数 - 理解文档内容

    ⚠️ 注意：不支持 macOS ARM 架构

    Args:
        image_path: 图片路径
        output_dir: 输出目录（可选）

    Returns:
        UnderstandingResult: 理解结果

    Example:
        >>> result = understand_document("contract.png")
        >>> print(f"分析完成: {result.success}")
    """
    with DocumentUnderstanding() as doc:
        return doc.understand(image_path, output_dir=output_dir)


def ask_document(
    image_path: Union[str, Path],
    question: str,
) -> str:
    """
    便捷函数 - 询问文档内容

    ⚠️ 注意：不支持 macOS ARM 架构

    Args:
        image_path: 图片路径
        question: 问题

    Returns:
        str: 答案

    Example:
        >>> answer = ask_document("contract.png", "合同金额是多少？")
        >>> print(answer)
    """
    with DocumentUnderstanding() as doc:
        result = doc.ask(image_path, question)
        return result.answer


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示文档理解功能

    该函数展示了 DocUnderstanding 的功能：
    1. 平台兼容性检查
    2. 文档内容理解
    3. 文档问答
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("DocUnderstanding 文档理解示例")
    logger.info("=" * 60)

    # 检查平台兼容性
    compatible, platform_info = check_doc_understanding_compatibility()

    logger.info("")
    logger.info(f"当前平台: {platform_info}")
    logger.info("")

    if not compatible:
        logger.warning("⚠️  警告: 文档理解功能可能需要 VLM 模型支持")
        logger.info("   VLM 模型不支持 macOS ARM")
        logger.info("")
        logger.info("替代方案:")
        logger.info("  - 使用 PP-StructureV3 进行文档解析")
        logger.info("  - 使用 PP-ChatOCRv4Doc 进行信息抽取")
        logger.info("")

    logger.info("功能说明:")
    logger.info("  - 深度理解文档内容")
    logger.info("  - 回答关于文档的问题")
    logger.info("  - 提取关键信息")
    logger.info("")
    logger.info("典型应用场景:")
    logger.info("  - 合同审查：「这份合同的有效期是多久？」")
    logger.info("  - 报告分析：「文档的主要结论是什么？」")
    logger.info("  - 表格理解：「表格中的最大值是多少？」")
    logger.info("")

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "understanding"

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备需要理解的文档图片")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    # 示例问题
    example_questions = [
        QuestionTemplates.GENERAL,
        QuestionTemplates.KEY_INFO,
        QuestionTemplates.DATE,
    ]

    logger.info("示例问题:")
    for q in example_questions:
        logger.info(f"  - {q}")
    logger.info("")

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 执行文档理解
        logger.info("【执行文档理解】")
        with DocumentUnderstanding() as doc:
            result = doc.understand(
                image_path,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("分析完成!")
                logger.info(f"共处理 {result.page_count} 页")
            else:
                logger.error(f"分析失败: {result.error}")

    except OCRPlatformError as e:
        logger.error(f"平台错误: {e}")
        logger.info("")
        logger.info("请在支持的平台上运行此示例，或使用替代方案")
        raise SystemExit(1) from e

    except OCRFileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        raise SystemExit(1) from e

    except OCRInitError as e:
        logger.error(f"初始化错误: {e}")
        logger.info("")
        logger.info("可能原因:")
        logger.info("  - VLM 模型不支持当前平台")
        logger.info("  - 缺少必要的依赖")
        logger.info("  - 内存不足")
        raise SystemExit(1) from e

    except OCRException as e:
        logger.error(f"OCR 错误: {e}")
        raise SystemExit(1) from e

    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
