#!/usr/bin/env python3
"""
PDF 转 Markdown 示例 - 使用 PP-StructureV3
PDF to Markdown Example

适用模型: PP-StructureV3
功能: 将 PDF 或图片文档转换为 Markdown 格式
API 版本: PaddleOCR 3.x
"""

from paddleocr import PPStructureV3
from pathlib import Path


def document_to_markdown(input_path: str, output_dir: str = None) -> str:
    """
    将文档（PDF/图片）转换为 Markdown (PaddleOCR 3.x)

    Args:
        input_path: 文档路径（PDF 或图片）
        output_dir: 输出目录

    Returns:
        Markdown 文本
    """
    # 初始化 PP-StructureV3
    pipeline = PPStructureV3(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_table_recognition=True,
        use_formula_recognition=False
    )

    # 执行预测
    output = pipeline.predict(input=input_path)

    # 收集所有页面的 Markdown
    markdown_list = []
    for res in output:
        markdown_list.append(res.markdown)

    # 合并多页（如果是 PDF）
    if len(markdown_list) > 1:
        markdown_text = pipeline.concatenate_markdown_pages(markdown_list)
    else:
        markdown_text = markdown_list[0] if markdown_list else ""

    # 保存结果
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 使用内置方法保存
        for res in pipeline.predict(input=input_path):
            res.save_to_markdown(save_path=str(output_path))
            res.save_to_json(save_path=str(output_path))

        print(f"结果已保存到: {output_path}")

    return markdown_text


def quick_convert(input_path: str, output_dir: str) -> None:
    """
    快速转换文档并保存 (PaddleOCR 3.x)

    Args:
        input_path: 文档路径
        output_dir: 输出目录
    """
    pipeline = PPStructureV3()

    output = pipeline.predict(input=input_path)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for res in output:
        # 打印结果
        res.print()
        # 保存 Markdown
        res.save_to_markdown(save_path=str(output_path))
        # 保存 JSON
        res.save_to_json(save_path=str(output_path))

    print(f"\n文件已保存到: {output_path}")


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "assets" / "outputs"

    print("=" * 50)
    print("PP-StructureV3 文档转换示例")
    print("=" * 50)
    print()

    # 示例：处理图片文档
    image_path = project_root / "assets" / "test_images" / "test.png"

    if image_path.exists():
        print(f"处理文档: {image_path}\n")

        # 方法 1: 快速转换
        quick_convert(str(image_path), str(output_dir))

        # 方法 2: 获取 Markdown 文本
        # markdown = document_to_markdown(str(image_path), str(output_dir))
        # print("\n--- Markdown 预览 ---")
        # print(markdown[:500] if len(markdown) > 500 else markdown)

    else:
        print(f"测试文档不存在: {image_path}")
        print("\n请准备以下文件之一进行测试:")
        print("  - assets/test_images/test.png (图片)")
        print("  - assets/test_images/document.pdf (PDF)")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
