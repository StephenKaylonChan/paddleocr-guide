#!/usr/bin/env python3
"""
图表识别示例 - 使用 PP-StructureV3
Chart Recognition Example

适用模型: PP-StructureV3
功能: 识别文档中的图表并提取数据
API 版本: PaddleOCR 3.x

测试图片要求:
- 包含图表的文档图片
- 支持类型：柱状图、折线图、饼图、散点图等
- 常见场景：报告、论文、PPT截图
"""

from paddleocr import PPStructureV3
from pathlib import Path


def recognize_chart(image_path: str, output_dir: str = None):
    """
    识别文档中的图表 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径（包含图表的文档）
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    # 初始化 PP-StructureV3（启用图表识别）
    pipeline = PPStructureV3(
        use_chart_recognition=True,      # 启用图表识别
        use_table_recognition=True,      # 同时启用表格（图表可能转为表格）
        use_formula_recognition=False,   # 禁用公式
        use_seal_recognition=False,      # 禁用印章
        use_doc_orientation_classify=False,
        use_doc_unwarping=False
    )

    print(f"正在识别图表: {image_path}")
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
            res.save_to_markdown(save_path=str(output_path))
            res.save_to_json(save_path=str(output_path))
            res.save_to_img(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")
        print("图表数据已转换为表格格式保存在 Markdown 文件中")

    return results


def extract_chart_data(image_path: str) -> list:
    """
    提取图表数据

    Args:
        image_path: 图片路径

    Returns:
        图表数据列表
    """
    pipeline = PPStructureV3(
        use_chart_recognition=True,
        use_table_recognition=True
    )

    output = pipeline.predict(input=image_path)

    chart_data = []
    for res in output:
        res_json = res.json
        # 从结果中提取图表信息
        if 'chart_res_list' in res_json:
            for chart in res_json['chart_res_list']:
                chart_data.append({
                    'type': chart.get('chart_type', 'unknown'),
                    'data': chart.get('chart_data', {})
                })

    return chart_data


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "chart"

    print("=" * 60)
    print("PP-StructureV3 图表识别示例")
    print("=" * 60)
    print()
    print("测试图片要求:")
    print("  - 包含图表的文档图片")
    print("  - 支持类型：柱状图、折线图、饼图、散点图等")
    print()
    print("输出格式:")
    print("  - 图表数据转换为表格")
    print("  - Markdown 和 JSON 格式保存")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备包含图表的文档图片")
        return

    # 识别图表
    results = recognize_chart(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("识别完成!")

    # 提取图表数据
    chart_data = extract_chart_data(str(image_path))
    if chart_data:
        print("\n识别到的图表:")
        for i, chart in enumerate(chart_data, 1):
            print(f"  [{i}] 类型: {chart['type']}")


if __name__ == "__main__":
    main()
