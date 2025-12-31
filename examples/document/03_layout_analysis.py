#!/usr/bin/env python3
"""
版面分析示例 - 使用 PP-StructureV3
Layout Analysis Example

适用模型: PP-StructureV3
功能: 分析文档版面结构（标题、段落、表格、图片等）
API 版本: PaddleOCR 3.x
"""

from paddleocr import PPStructureV3
from pathlib import Path
import json


def analyze_layout(image_path: str, output_dir: str = None):
    """
    分析文档版面 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    # 初始化 PP-StructureV3（完整版面分析）
    pipeline = PPStructureV3(
        use_doc_orientation_classify=True,  # 文档方向分类
        use_doc_unwarping=False,            # 文档弯曲矫正
        use_table_recognition=True,         # 表格识别
        use_formula_recognition=True,       # 公式识别
        use_seal_recognition=False,         # 印章识别
        use_chart_recognition=False         # 图表识别
    )

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

            # 保存 Markdown
            res.save_to_markdown(save_path=str(output_path))

            # 保存 JSON
            res.save_to_json(save_path=str(output_path))

            # 保存可视化图片
            res.save_to_img(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return results


def quick_analysis(image_path: str) -> None:
    """
    快速版面分析（仅输出不保存）

    Args:
        image_path: 图片路径
    """
    pipeline = PPStructureV3()

    output = pipeline.predict(input=image_path)

    print("\n版面分析结果:")
    print("-" * 50)

    for res in output:
        res.print()


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs"

    print("=" * 60)
    print("PP-StructureV3 版面分析示例")
    print("=" * 60)
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备文档图片进行测试")
        return

    print(f"分析文档: {image_path}\n")

    # 执行版面分析
    results = analyze_layout(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("分析完成!")
    print(f"共处理 {len(results)} 页")


if __name__ == "__main__":
    main()
