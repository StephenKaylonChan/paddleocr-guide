#!/usr/bin/env python3
"""
印章识别示例 - 使用 PP-StructureV3
Seal/Stamp Recognition Example

适用模型: PP-StructureV3
功能: 识别文档中的印章/公章文字
API 版本: PaddleOCR 3.x

测试图片要求:
- 包含红色或蓝色印章的文档图片
- 常见场景：合同、证书、公文等
"""

from paddleocr import PPStructureV3
from pathlib import Path


def recognize_seal(image_path: str, output_dir: str = None):
    """
    识别文档中的印章文字 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径（包含印章的文档）
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    # 初始化 PP-StructureV3（启用印章识别）
    pipeline = PPStructureV3(
        use_seal_recognition=True,       # 启用印章识别
        use_table_recognition=False,     # 禁用表格（提高速度）
        use_formula_recognition=False,   # 禁用公式
        use_chart_recognition=False,     # 禁用图表
        use_doc_orientation_classify=False,
        use_doc_unwarping=False
    )

    print(f"正在识别印章: {image_path}")
    print("=" * 50)

    # 执行预测
    output = pipeline.predict(input=image_path)

    results = []
    for res in output:
        results.append(res)

        # 打印结果
        res.print()

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 保存结果
            res.save_to_json(save_path=str(output_path))
            res.save_to_img(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return results


def extract_seal_text(image_path: str) -> list:
    """
    提取印章中的文字内容

    Args:
        image_path: 图片路径

    Returns:
        印章文字列表
    """
    pipeline = PPStructureV3(
        use_seal_recognition=True,
        use_table_recognition=False,
        use_formula_recognition=False
    )

    output = pipeline.predict(input=image_path)

    seal_texts = []
    for res in output:
        # 从 JSON 结果中提取印章文字
        res_json = res.json
        if 'seal_res_list' in res_json:
            for seal in res_json['seal_res_list']:
                if 'rec_texts' in seal:
                    seal_texts.extend(seal['rec_texts'])

    return seal_texts


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "seal"

    print("=" * 60)
    print("PP-StructureV3 印章识别示例")
    print("=" * 60)
    print()
    print("测试图片要求:")
    print("  - 包含印章/公章的文档图片")
    print("  - 常见场景：合同、证书、公文")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备包含印章的文档图片")
        print("将图片放置于: assets/test_images/")
        return

    # 识别印章
    results = recognize_seal(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("识别完成!")
    print(f"共处理 {len(results)} 页")

    # 提取印章文字
    seal_texts = extract_seal_text(str(image_path))
    if seal_texts:
        print("\n印章文字内容:")
        for text in seal_texts:
            print(f"  - {text}")


if __name__ == "__main__":
    main()
