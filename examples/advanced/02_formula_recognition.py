#!/usr/bin/env python3
"""
公式识别示例 - 使用 PP-StructureV3
Mathematical Formula Recognition Example

适用模型: PP-StructureV3
功能: 识别文档中的数学公式并转换为 LaTeX
API 版本: PaddleOCR 3.x

测试图片要求:
- 包含数学公式的文档图片
- 常见场景：教材、论文、试卷、笔记
"""

from paddleocr import PPStructureV3
from pathlib import Path


def recognize_formula(image_path: str, output_dir: str = None):
    """
    识别文档中的数学公式 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径（包含公式的文档）
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    # 初始化 PP-StructureV3（启用公式识别）
    pipeline = PPStructureV3(
        use_formula_recognition=True,    # 启用公式识别
        use_table_recognition=False,     # 禁用表格
        use_seal_recognition=False,      # 禁用印章
        use_chart_recognition=False,     # 禁用图表
        use_doc_orientation_classify=False,
        use_doc_unwarping=False
    )

    print(f"正在识别公式: {image_path}")
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

            # 保存为 Markdown（公式转为 LaTeX）
            res.save_to_markdown(save_path=str(output_path))
            res.save_to_json(save_path=str(output_path))
            res.save_to_img(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")
        print("公式已转换为 LaTeX 格式保存在 Markdown 文件中")

    return results


def extract_formulas(image_path: str) -> list:
    """
    提取文档中的公式（LaTeX 格式）

    Args:
        image_path: 图片路径

    Returns:
        公式列表（LaTeX 格式）
    """
    pipeline = PPStructureV3(
        use_formula_recognition=True,
        use_table_recognition=False
    )

    output = pipeline.predict(input=image_path)

    formulas = []
    for res in output:
        res_json = res.json
        # 从结果中提取公式
        if 'formula_res_list' in res_json:
            for formula in res_json['formula_res_list']:
                if 'rec_formula' in formula:
                    formulas.append(formula['rec_formula'])

    return formulas


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "formula"

    print("=" * 60)
    print("PP-StructureV3 公式识别示例")
    print("=" * 60)
    print()
    print("测试图片要求:")
    print("  - 包含数学公式的文档图片")
    print("  - 常见场景：教材、论文、试卷")
    print()
    print("输出格式:")
    print("  - Markdown 文件（公式转为 LaTeX）")
    print("  - JSON 文件（详细结构信息）")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备包含数学公式的文档图片")
        return

    # 识别公式
    results = recognize_formula(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("识别完成!")

    # 提取公式
    formulas = extract_formulas(str(image_path))
    if formulas:
        print("\n识别到的公式 (LaTeX):")
        for i, formula in enumerate(formulas, 1):
            print(f"  [{i}] {formula}")


if __name__ == "__main__":
    main()
