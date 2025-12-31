#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能信息抽取示例 - 使用 PP-ChatOCRv4Doc
Intelligent Information Extraction Example

本示例演示了如何使用 PP-ChatOCRv4Doc 从文档中智能提取关键信息。
PP-ChatOCRv4Doc 使用离线模式（PP-DocBee2），无需 API Key 即可运行。

支持的文档类型：
- 票据类：发票、收据、银行回单
- 证件类：身份证、营业执照、资质证书
- 合同类：合同首页、协议书

This example demonstrates how to use PP-ChatOCRv4Doc to intelligently
extract key information from documents. It uses offline mode (PP-DocBee2)
and does not require an API key.

适用模型: PP-ChatOCRv4Doc (离线模式 PP-DocBee2)
支持系统: macOS (含 ARM) / Linux / Windows
API 版本: PaddleOCR 3.x
作者: paddleocr-guide

使用方法:
    python examples/advanced/04_chatocr_extraction.py

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
# 预设提示词模板
# Predefined Prompt Templates
# =============================================================================


class ExtractionTemplates:
    """预设的信息抽取提示词模板"""

    # 发票信息提取
    INVOICE = (
        "请提取以下信息："
        "发票号码、发票代码、开票日期、"
        "购买方名称、销售方名称、"
        "金额、税额、价税合计"
    )

    # 身份证信息提取
    ID_CARD = "请提取以下信息：" "姓名、性别、民族、出生日期、住址、身份证号码"

    # 营业执照信息提取
    BUSINESS_LICENSE = (
        "请提取以下信息："
        "公司名称、统一社会信用代码、法定代表人、"
        "注册资本、成立日期、营业期限、经营范围"
    )

    # 合同信息提取
    CONTRACT = "请提取以下信息：" "合同编号、甲方名称、乙方名称、" "签订日期、合同金额、合同期限"

    # 银行回单信息提取
    BANK_RECEIPT = (
        "请提取以下信息：" "交易日期、交易流水号、付款方、收款方、" "交易金额、交易类型、摘要"
    )

    # 通用文档分析
    GENERAL = "请分析这个文档，提取所有关键信息"


# =============================================================================
# 数据类定义
# Data Class Definitions
# =============================================================================


@dataclass
class ExtractionResult:
    """
    信息抽取结果

    Attributes:
        source_file: 源文件路径
        prompt: 使用的提示词
        extracted_info: 抽取到的信息（字典格式）
        raw_response: 原始响应
        page_count: 页数
        success: 是否成功
        error: 错误信息
    """

    source_file: str
    prompt: str = ""
    extracted_info: dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Any] = None
    page_count: int = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def has_info(self) -> bool:
        """是否有提取到的信息"""
        return bool(self.extracted_info)

    def get(self, key: str, default: Any = None) -> Any:
        """获取指定的抽取信息"""
        return self.extracted_info.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "source_file": self.source_file,
            "prompt": self.prompt,
            "extracted_info": self.extracted_info,
            "page_count": self.page_count,
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# 智能信息抽取器类
# Intelligent Information Extractor Class
# =============================================================================


class IntelligentExtractor:
    """
    智能信息抽取器 - 从文档中提取关键信息

    该类封装了 PP-ChatOCRv4Doc 的信息抽取功能，支持：
    - 票据信息提取（发票、收据、银行回单）
    - 证件信息提取（身份证、营业执照）
    - 合同信息提取
    - 自定义提示词提取

    使用离线模式（PP-DocBee2），无需 API Key。

    Attributes:
        use_seal_recognition: 是否启用印章识别
        use_table_recognition: 是否启用表格识别
        use_doc_orientation_classify: 是否启用文档方向分类
        use_doc_unwarping: 是否启用文档弯曲矫正

    Example:
        >>> with IntelligentExtractor() as extractor:
        ...     # 使用预设模板
        ...     result = extractor.extract_invoice("invoice.png")
        ...     print(f"发票号码: {result.get('发票号码')}")
        ...
        ...     # 使用自定义提示
        ...     result = extractor.extract("document.png", prompt="提取日期和金额")
    """

    def __init__(
        self,
        *,
        use_seal_recognition: bool = True,
        use_table_recognition: bool = True,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
    ) -> None:
        """
        初始化智能信息抽取器

        Args:
            use_seal_recognition: 是否启用印章识别（对票据和合同有帮助）
            use_table_recognition: 是否启用表格识别
            use_doc_orientation_classify: 是否启用文档方向分类
            use_doc_unwarping: 是否启用文档弯曲矫正
        """
        self.use_seal_recognition = use_seal_recognition
        self.use_table_recognition = use_table_recognition
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping

        self._pipeline: Optional[Any] = None
        self._initialized: bool = False

    def initialize(self) -> "IntelligentExtractor":
        """初始化 PP-ChatOCRv4Doc 引擎"""
        if self._initialized:
            return self

        logger.info("正在初始化智能信息抽取引擎...")
        logger.info("运行模式: 离线 (PP-DocBee2)，无需 API Key")

        try:
            from paddleocr import PPChatOCRv4Doc

            self._pipeline = PPChatOCRv4Doc(
                use_seal_recognition=self.use_seal_recognition,
                use_table_recognition=self.use_table_recognition,
                use_doc_orientation_classify=self.use_doc_orientation_classify,
                use_doc_unwarping=self.use_doc_unwarping,
            )
            self._initialized = True
            logger.info("智能信息抽取引擎初始化完成")
            return self

        except ImportError as e:
            raise OCRInitError(
                "PaddleOCR 未安装，请运行: pip install paddleocr",
                error_code="E103",
            ) from e

        except Exception as e:
            raise OCRInitError(
                f"智能信息抽取引擎初始化失败: {e}",
                error_code="E102",
            ) from e

    def cleanup(self) -> None:
        """清理资源"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._initialized = False
            gc.collect()

    def __enter__(self) -> "IntelligentExtractor":
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cleanup()
        return False

    def extract(
        self,
        image_path: Union[str, Path],
        *,
        prompt: Optional[str] = None,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> ExtractionResult:
        """
        从文档中提取信息

        Args:
            image_path: 图片路径
            prompt: 提取提示词（如 "提取发票号码、金额、日期"）
            output_dir: 输出目录（可选）

        Returns:
            ExtractionResult: 抽取结果

        Raises:
            OCRFileNotFoundError: 文件不存在
            OCRInitError: 引擎未初始化
        """
        if not self._initialized:
            raise OCRInitError("智能信息抽取引擎未初始化")

        path = Path(image_path)
        if not path.exists():
            raise OCRFileNotFoundError(
                f"文件不存在: {path}",
                file_path=str(path),
            )

        # 使用默认提示词
        if not prompt:
            prompt = ExtractionTemplates.GENERAL

        logger.info(f"正在分析文档: {path.name}")
        logger.info(f"提取目标: {prompt[:50]}..." if len(prompt) > 50 else f"提取目标: {prompt}")

        try:
            # 执行预测
            if prompt:
                output = self._pipeline.predict(input=str(path), prompt=prompt)
            else:
                output = self._pipeline.predict(input=str(path))

            extracted_info: dict[str, Any] = {}
            page_count = 0

            # 准备输出目录
            if output_dir:
                output_path = ensure_directory(output_dir)

            for res in output:
                page_count += 1

                # 打印结果
                res.print()

                # 获取 JSON 结果
                try:
                    res_json = res.json
                    if isinstance(res_json, dict):
                        extracted_info.update(res_json)
                except Exception as e:
                    logger.warning(f"解析抽取结果时出错: {e}")

                # 保存结果
                if output_dir:
                    try:
                        res.save_to_json(save_path=str(output_path))
                        res.save_to_markdown(save_path=str(output_path))
                    except Exception as e:
                        logger.warning(f"保存结果时出错: {e}")

            logger.info(f"分析完成，共处理 {page_count} 页")

            if output_dir:
                logger.info(f"结果已保存到: {output_path}")

            return ExtractionResult(
                source_file=str(path),
                prompt=prompt,
                extracted_info=extracted_info,
                page_count=page_count,
            )

        except OCRException:
            raise
        except Exception as e:
            logger.error(f"信息抽取失败: {e}")
            return ExtractionResult(
                source_file=str(path),
                prompt=prompt,
                success=False,
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # 预设模板方法
    # Predefined Template Methods
    # -------------------------------------------------------------------------

    def extract_invoice(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> ExtractionResult:
        """
        提取发票信息

        Args:
            image_path: 发票图片路径
            output_dir: 输出目录（可选）

        Returns:
            ExtractionResult: 包含发票号码、金额、日期等信息
        """
        return self.extract(
            image_path,
            prompt=ExtractionTemplates.INVOICE,
            output_dir=output_dir,
        )

    def extract_id_card(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> ExtractionResult:
        """
        提取身份证信息

        Args:
            image_path: 身份证图片路径
            output_dir: 输出目录（可选）

        Returns:
            ExtractionResult: 包含姓名、身份证号等信息
        """
        return self.extract(
            image_path,
            prompt=ExtractionTemplates.ID_CARD,
            output_dir=output_dir,
        )

    def extract_business_license(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> ExtractionResult:
        """
        提取营业执照信息

        Args:
            image_path: 营业执照图片路径
            output_dir: 输出目录（可选）

        Returns:
            ExtractionResult: 包含公司名称、统一社会信用代码等信息
        """
        return self.extract(
            image_path,
            prompt=ExtractionTemplates.BUSINESS_LICENSE,
            output_dir=output_dir,
        )

    def extract_contract(
        self,
        image_path: Union[str, Path],
        *,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> ExtractionResult:
        """
        提取合同信息

        Args:
            image_path: 合同图片路径
            output_dir: 输出目录（可选）

        Returns:
            ExtractionResult: 包含合同编号、甲乙方等信息
        """
        return self.extract(
            image_path,
            prompt=ExtractionTemplates.CONTRACT,
            output_dir=output_dir,
        )


# =============================================================================
# 便捷函数
# Convenience Functions
# =============================================================================


def extract_document_info(
    image_path: Union[str, Path],
    *,
    prompt: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> ExtractionResult:
    """
    便捷函数 - 从文档中提取信息

    Args:
        image_path: 图片路径
        prompt: 提取提示词（可选）
        output_dir: 输出目录（可选）

    Returns:
        ExtractionResult: 抽取结果

    Example:
        >>> result = extract_document_info(
        ...     "invoice.png",
        ...     prompt="提取发票号码和金额"
        ... )
        >>> print(result.extracted_info)
    """
    with IntelligentExtractor() as extractor:
        return extractor.extract(image_path, prompt=prompt, output_dir=output_dir)


# =============================================================================
# 主函数
# Main Function
# =============================================================================


def main() -> None:
    """
    主函数 - 演示智能信息抽取功能

    该函数展示了 PP-ChatOCRv4Doc 的信息抽取功能：
    1. 离线模式运行，无需 API Key
    2. 支持多种文档类型
    3. 支持自定义提示词
    """
    # 配置日志系统
    setup_logging()

    logger.info("=" * 60)
    logger.info("PP-ChatOCRv4Doc 智能信息抽取示例")
    logger.info("=" * 60)

    # 设置路径
    image_path = PATH_CONFIG.test_images_dir / "test.png"
    output_dir = PATH_CONFIG.outputs_dir / "chatocr"

    # 打印说明
    logger.info("")
    logger.info("运行模式: 离线 (PP-DocBee2)")
    logger.info("无需 API Key")
    logger.info("")
    logger.info("测试图片要求:")
    logger.info("  - 票据类：发票、收据、银行回单")
    logger.info("  - 证件类：身份证、营业执照")
    logger.info("  - 合同类：合同、协议书")
    logger.info("")
    logger.info("预设提取模板:")
    logger.info("  - extract_invoice(): 发票信息")
    logger.info("  - extract_id_card(): 身份证信息")
    logger.info("  - extract_business_license(): 营业执照信息")
    logger.info("  - extract_contract(): 合同信息")
    logger.info("")

    # 检查测试文件
    if not image_path.exists():
        logger.warning(f"测试图片不存在: {image_path}")
        logger.info("请准备票据、证件或合同图片进行测试")
        logger.info(f"将图片放置于: {PATH_CONFIG.test_images_dir}")
        return

    try:
        logger.info(f"处理图片: {image_path.name}")
        logger.info("")

        # 使用智能信息抽取器
        with IntelligentExtractor() as extractor:
            # 通用信息提取
            logger.info("执行通用文档分析...")
            result = extractor.extract(
                image_path,
                prompt=ExtractionTemplates.GENERAL,
                output_dir=output_dir,
            )

            if result.success:
                logger.info("")
                logger.info("=" * 60)
                logger.info("分析完成!")
                logger.info(f"共处理 {result.page_count} 页")

                if result.has_info:
                    logger.info("")
                    logger.info("抽取到的信息:")
                    for key, value in result.extracted_info.items():
                        # 截取长值
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        logger.info(f"  {key}: {value}")
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
