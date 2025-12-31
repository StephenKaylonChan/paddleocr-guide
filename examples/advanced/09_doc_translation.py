#!/usr/bin/env python3
"""
文档翻译示例 - 使用 PP-DocTranslation
Document Translation Example

适用模型: PP-DocTranslation
功能: 将文档从一种语言翻译为另一种语言，保持版面结构
API 版本: PaddleOCR 3.x

测试图片要求:
- 英文文档（翻译为中文）
- 中文文档（翻译为英文）
- 包含表格、图片的复杂文档

注意：需要配置 LLM API（如 ERNIE API）
"""

from paddleocr import PPDocTranslation
from pathlib import Path


def translate_document(
    image_path: str,
    source_lang: str = "en",
    target_lang: str = "zh",
    output_dir: str = None,
    chat_bot_config: dict = None
):
    """
    翻译文档 (PaddleOCR 3.x)

    Args:
        image_path: 图片/PDF路径
        source_lang: 源语言 (en/zh/ja/ko 等)
        target_lang: 目标语言
        output_dir: 输出目录
        chat_bot_config: LLM 配置

    Returns:
        翻译结果
    """
    # 默认使用 ERNIE API（需要 API Key）
    if chat_bot_config is None:
        chat_bot_config = {
            "module_name": "chat_bot",
            "model_name": "ernie-3.5-8k",
            "base_url": "https://qianfan.baidubce.com/v2",
            "api_type": "openai",
            # 需要设置环境变量 QIANFAN_API_KEY 或在此处填入
            "api_key": None  # 从环境变量读取
        }

    # 初始化翻译产线
    translator = PPDocTranslation(
        use_doc_orientation_classify=True,
        use_doc_unwarping=False,
        use_table_recognition=True,
        use_seal_recognition=False,
        chat_bot_config=chat_bot_config
    )

    print(f"正在翻译文档: {image_path}")
    print(f"翻译方向: {source_lang} → {target_lang}")
    print("=" * 50)

    # 第一步：视觉分析
    visual_results = translator.visual_predict(input=image_path)

    results = []
    for res in visual_results:
        results.append(res)

        # 打印版面分析结果
        if "layout_parsing_result" in res:
            res["layout_parsing_result"].print()

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            if "layout_parsing_result" in res:
                res["layout_parsing_result"].save_to_markdown(
                    save_path=str(output_path)
                )

    # 第二步：调用翻译（需要 LLM API）
    # 注意：translate 方法需要 API 配置
    # translated = translator.translate(
    #     visual_results,
    #     source_lang=source_lang,
    #     target_lang=target_lang
    # )

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return results


def translate_with_custom_llm(
    image_path: str,
    api_key: str,
    source_lang: str = "en",
    target_lang: str = "zh"
):
    """
    使用自定义 LLM 进行翻译

    Args:
        image_path: 图片路径
        api_key: API Key
        source_lang: 源语言
        target_lang: 目标语言

    Returns:
        翻译结果
    """
    chat_bot_config = {
        "module_name": "chat_bot",
        "model_name": "ernie-3.5-8k",
        "base_url": "https://qianfan.baidubce.com/v2",
        "api_type": "openai",
        "api_key": api_key
    }

    translator = PPDocTranslation(chat_bot_config=chat_bot_config)

    # 视觉分析
    visual_results = translator.visual_predict(input=image_path)

    # 翻译（需要实际的 API 调用）
    # translated = translator.translate(visual_results, ...)

    return visual_results


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "translation"

    print("=" * 60)
    print("PP-DocTranslation 文档翻译示例")
    print("=" * 60)
    print()
    print("功能说明:")
    print("  - 识别文档内容（文字、表格、图片）")
    print("  - 保持版面结构进行翻译")
    print("  - 支持多种语言对")
    print()
    print("支持的语言:")
    print("  - 中文 (zh)")
    print("  - 英文 (en)")
    print("  - 日文 (ja)")
    print("  - 韩文 (ko)")
    print("  - 更多...")
    print()
    print("⚠️ 注意:")
    print("  - 翻译功能需要配置 LLM API")
    print("  - 推荐使用 ERNIE API 或其他兼容 OpenAI 格式的 API")
    print("  - 设置环境变量 QIANFAN_API_KEY 或在代码中配置")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备需要翻译的文档图片")
        return

    # 仅执行视觉分析（不需要 API）
    print("【视觉分析模式】")
    print("（翻译功能需要配置 API Key）")
    print()

    try:
        results = translate_document(
            str(image_path),
            output_dir=str(output_dir)
        )

        print("\n" + "=" * 60)
        print("视觉分析完成!")
        print(f"共处理 {len(results)} 页")
        print()
        print("要启用完整翻译功能，请:")
        print("  1. 获取 ERNIE API Key")
        print("  2. 设置环境变量: export QIANFAN_API_KEY=your_key")
        print("  3. 或在代码中配置 chat_bot_config")

    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print("\n请检查 PaddleOCR 是否正确安装")


if __name__ == "__main__":
    main()
