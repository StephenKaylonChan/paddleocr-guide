#!/usr/bin/env python3
"""
智能信息抽取示例 - 使用 PP-ChatOCRv4Doc
Intelligent Information Extraction Example

适用模型: PP-ChatOCRv4Doc (离线模式 PP-DocBee2)
功能: 从票据、证件、合同等文档中智能提取关键信息
API 版本: PaddleOCR 3.x

测试图片要求:
- 票据类：发票、收据、银行回单
- 证件类：身份证、营业执照、资质证书
- 合同类：合同首页、协议书

注意：使用离线模式，无需 API Key
"""

from paddleocr import PPChatOCRv4Doc
from pathlib import Path


def extract_document_info(image_path: str, prompt: str = None, output_dir: str = None):
    """
    智能提取文档信息 (PaddleOCR 3.x - 离线模式)

    Args:
        image_path: 图片路径
        prompt: 提取提示（如 "提取发票号码、金额、日期"）
        output_dir: 输出目录

    Returns:
        提取结果
    """
    # 初始化 PP-ChatOCRv4Doc（离线模式）
    chat_ocr = PPChatOCRv4Doc(
        use_seal_recognition=True,       # 启用印章识别
        use_table_recognition=True,      # 启用表格识别
        use_doc_orientation_classify=False,
        use_doc_unwarping=False
    )

    print(f"正在分析文档: {image_path}")
    if prompt:
        print(f"提取目标: {prompt}")
    print("=" * 50)

    # 执行预测
    if prompt:
        output = chat_ocr.predict(input=image_path, prompt=prompt)
    else:
        output = chat_ocr.predict(input=image_path)

    results = []
    for res in output:
        results.append(res)

        # 打印结果
        res.print()

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            res.save_to_json(save_path=str(output_path))
            res.save_to_markdown(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return results


def extract_invoice_info(image_path: str) -> dict:
    """
    提取发票信息

    Args:
        image_path: 发票图片路径

    Returns:
        发票信息字典
    """
    prompt = "请提取以下信息：发票号码、发票代码、开票日期、购买方名称、销售方名称、金额、税额、价税合计"

    chat_ocr = PPChatOCRv4Doc(use_seal_recognition=True)
    output = chat_ocr.predict(input=image_path, prompt=prompt)

    for res in output:
        return res.json

    return {}


def extract_id_card_info(image_path: str) -> dict:
    """
    提取身份证信息

    Args:
        image_path: 身份证图片路径

    Returns:
        身份证信息字典
    """
    prompt = "请提取以下信息：姓名、性别、民族、出生日期、住址、身份证号码"

    chat_ocr = PPChatOCRv4Doc()
    output = chat_ocr.predict(input=image_path, prompt=prompt)

    for res in output:
        return res.json

    return {}


def extract_contract_info(image_path: str) -> dict:
    """
    提取合同信息

    Args:
        image_path: 合同图片路径

    Returns:
        合同信息字典
    """
    prompt = "请提取以下信息：合同编号、甲方名称、乙方名称、签订日期、合同金额、合同期限"

    chat_ocr = PPChatOCRv4Doc(use_seal_recognition=True)
    output = chat_ocr.predict(input=image_path, prompt=prompt)

    for res in output:
        return res.json

    return {}


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "chatocr"

    print("=" * 60)
    print("PP-ChatOCRv4Doc 智能信息抽取示例")
    print("=" * 60)
    print()
    print("运行模式: 离线 (PP-DocBee2)")
    print("无需 API Key")
    print()
    print("测试图片要求:")
    print("  - 票据类：发票、收据、银行回单")
    print("  - 证件类：身份证、营业执照")
    print("  - 合同类：合同、协议书")
    print()
    print("预设提取模板:")
    print("  - extract_invoice_info(): 发票信息")
    print("  - extract_id_card_info(): 身份证信息")
    print("  - extract_contract_info(): 合同信息")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备票据、证件或合同图片进行测试")
        return

    # 通用信息提取
    print("执行通用文档分析...")
    results = extract_document_info(
        str(image_path),
        prompt="请分析这个文档，提取所有关键信息",
        output_dir=str(output_dir)
    )

    print("\n" + "=" * 60)
    print("分析完成!")
    print(f"共处理 {len(results)} 页")


if __name__ == "__main__":
    main()
