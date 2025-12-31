#!/usr/bin/env python3
"""
表格识别示例 - 使用 PP-StructureV3
Table Recognition Example

适用模型: PP-StructureV3
功能: 识别图片中的表格并导出为多种格式
API 版本: PaddleOCR 3.x
"""

from paddleocr import PPStructureV3
from pathlib import Path
import json


def recognize_tables(image_path: str) -> list:
    """
    识别图片中的所有表格 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径

    Returns:
        结果对象列表
    """
    # 初始化 PP-StructureV3（仅启用表格识别）
    pipeline = PPStructureV3(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_table_recognition=True,
        use_formula_recognition=False,
        use_seal_recognition=False,
        use_chart_recognition=False
    )

    # 执行预测
    output = pipeline.predict(input=image_path)

    return list(output)


def process_table_image(image_path: str, output_dir: str = None) -> dict:
    """
    处理包含表格的图片 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        处理结果
    """
    print(f"处理图片: {image_path}")

    # 识别表格
    results = recognize_tables(image_path)

    result_info = {
        'image': str(image_path),
        'page_count': len(results)
    }

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    for idx, res in enumerate(results):
        print(f"\n--- 第 {idx + 1} 页 ---")

        # 打印识别结果
        res.print()

        if output_dir:
            # 保存为 Markdown（包含表格）
            res.save_to_markdown(save_path=str(output_path))
            print(f"Markdown 已保存")

            # 保存为 JSON
            res.save_to_json(save_path=str(output_path))
            print(f"JSON 已保存")

            # 保存可视化图片
            res.save_to_img(save_path=str(output_path))
            print(f"可视化图片已保存")

    if output_dir:
        print(f"\n所有结果已保存到: {output_path}")

    return result_info


def table_html_to_csv(html_content: str, output_path: str) -> bool:
    """
    将表格 HTML 转换为 CSV（可选功能）

    Args:
        html_content: 表格的 HTML 代码
        output_path: 输出 CSV 路径

    Returns:
        是否成功
    """
    try:
        import pandas as pd
        from io import StringIO

        # 使用 pandas 解析 HTML 表格
        dfs = pd.read_html(StringIO(html_content))
        if dfs:
            dfs[0].to_csv(output_path, index=False, encoding='utf-8')
            print(f"CSV 已保存: {output_path}")
            return True
    except ImportError:
        print("提示: 安装 pandas 可启用 CSV 导出功能")
        print("运行: pip install pandas")
    except Exception as e:
        print(f"转换失败: {e}")

    return False


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs"

    print("=" * 50)
    print("PP-StructureV3 表格识别示例")
    print("=" * 50)
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备包含表格的图片进行测试")
        print("将图片放置于: assets/test_images/")
        return

    result = process_table_image(str(image_path), str(output_dir))

    print("\n" + "=" * 50)
    print("处理完成!")


if __name__ == "__main__":
    main()
