#!/usr/bin/env python3
"""
PDF 转 Markdown 示例 - 使用 PP-StructureV3
PDF to Markdown Example

适用模型: PP-StructureV3
功能: 将 PDF 文档转换为 Markdown 格式
"""

from paddleocr import PPStructure
from pathlib import Path
import json


def pdf_to_markdown(pdf_path: str, output_dir: str = None) -> str:
    """
    将 PDF 转换为 Markdown

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录

    Returns:
        Markdown 文本
    """
    # 初始化 PP-Structure
    structure = PPStructure(
        recovery=True,  # 启用版面恢复
        show_log=False
    )

    # 处理 PDF
    result = structure(pdf_path)

    # 构建 Markdown
    markdown_parts = []

    for item in result:
        item_type = item.get('type', '')

        if item_type == 'title':
            # 标题
            text = item.get('res', {}).get('text', '')
            markdown_parts.append(f"# {text}\n")

        elif item_type == 'text':
            # 正文
            text = item.get('res', {}).get('text', '')
            markdown_parts.append(f"{text}\n")

        elif item_type == 'table':
            # 表格（HTML 格式）
            html = item.get('res', {}).get('html', '')
            markdown_parts.append(f"\n{html}\n")

        elif item_type == 'figure':
            # 图片
            markdown_parts.append("\n[图片]\n")

    markdown_text = '\n'.join(markdown_parts)

    # 保存结果
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存 Markdown
        md_file = output_path / f"{Path(pdf_path).stem}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        print(f"Markdown 已保存: {md_file}")

        # 保存原始 JSON 结果
        json_file = output_path / f"{Path(pdf_path).stem}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            # 转换为可序列化格式
            serializable_result = []
            for item in result:
                serializable_result.append({
                    'type': item.get('type'),
                    'bbox': item.get('bbox'),
                    'res': str(item.get('res', ''))[:500]  # 截断长内容
                })
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
        print(f"JSON 已保存: {json_file}")

    return markdown_text


def process_image_as_document(image_path: str, output_dir: str = None) -> str:
    """
    将图片作为文档处理

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        Markdown 文本
    """
    # 初始化 PP-Structure
    structure = PPStructure(
        recovery=True,
        show_log=False
    )

    # 处理图片
    result = structure(image_path)

    # 构建 Markdown
    markdown_parts = ["# 文档识别结果\n"]

    for idx, item in enumerate(result, 1):
        item_type = item.get('type', 'unknown')

        if item_type == 'table':
            markdown_parts.append(f"\n## 表格 {idx}\n")
            html = item.get('res', {}).get('html', '')
            markdown_parts.append(html)
        elif item_type == 'text':
            text = item.get('res', {}).get('text', '')
            if text:
                markdown_parts.append(f"\n{text}\n")
        elif item_type == 'title':
            text = item.get('res', {}).get('text', '')
            markdown_parts.append(f"\n## {text}\n")

    markdown_text = '\n'.join(markdown_parts)

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        md_file = output_path / f"{Path(image_path).stem}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        print(f"Markdown 已保存: {md_file}")

    return markdown_text


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
        print(f"处理图片: {image_path}\n")
        markdown = process_image_as_document(str(image_path), str(output_dir))
        print("\n--- Markdown 预览 ---")
        print(markdown[:500])
        if len(markdown) > 500:
            print("...")
    else:
        print(f"测试图片不存在: {image_path}")
        print("\n请准备以下文件之一进行测试:")
        print("  - assets/test_images/test.png (图片)")
        print("  - assets/test_images/document.pdf (PDF)")

    print("\n" + "=" * 50)
    print("提示: 如需处理 PDF，请使用 pdf_to_markdown() 函数")


if __name__ == "__main__":
    main()
