#!/usr/bin/env python3
"""
版面分析示例 - 使用 PP-StructureV3
Layout Analysis Example

适用模型: PP-StructureV3
功能: 分析文档版面结构（标题、段落、表格、图片等）
"""

from paddleocr import PPStructure
from pathlib import Path
import json


# 版面元素类型
LAYOUT_TYPES = {
    'text': '正文',
    'title': '标题',
    'table': '表格',
    'figure': '图片',
    'list': '列表',
    'reference': '参考文献',
    'header': '页眉',
    'footer': '页脚',
    'equation': '公式'
}


def analyze_layout(image_path: str) -> list:
    """
    分析文档版面

    Args:
        image_path: 图片路径

    Returns:
        版面元素列表
    """
    # 初始化 PP-Structure
    structure = PPStructure(
        layout=True,     # 启用版面分析
        table=True,      # 启用表格识别
        show_log=False
    )

    # 分析
    result = structure(image_path)

    # 解析结果
    elements = []
    for idx, item in enumerate(result):
        element = {
            'index': idx,
            'type': item.get('type', 'unknown'),
            'type_name': LAYOUT_TYPES.get(item.get('type'), '未知'),
            'bbox': item.get('bbox', []),
        }

        # 提取内容
        res = item.get('res', {})
        if isinstance(res, dict):
            if 'text' in res:
                element['text'] = res['text']
            if 'html' in res:
                element['html'] = res['html'][:100] + '...' if len(res.get('html', '')) > 100 else res.get('html', '')
        elif isinstance(res, str):
            element['text'] = res

        elements.append(element)

    return elements


def visualize_layout(elements: list) -> str:
    """
    生成版面结构的文本可视化

    Args:
        elements: 版面元素列表

    Returns:
        可视化文本
    """
    lines = []
    lines.append("=" * 60)
    lines.append("文档版面结构")
    lines.append("=" * 60)

    # 按类型统计
    type_counts = {}
    for elem in elements:
        t = elem['type_name']
        type_counts[t] = type_counts.get(t, 0) + 1

    lines.append("\n【统计】")
    for t, count in type_counts.items():
        lines.append(f"  {t}: {count} 个")

    lines.append("\n【详细列表】")
    lines.append("-" * 60)

    for elem in elements:
        lines.append(f"\n[{elem['index'] + 1}] {elem['type_name']} ({elem['type']})")

        # 位置信息
        if elem['bbox']:
            bbox = elem['bbox']
            lines.append(f"    位置: ({bbox[0]:.0f}, {bbox[1]:.0f}) - ({bbox[2]:.0f}, {bbox[3]:.0f})")

        # 内容预览
        if 'text' in elem:
            text = elem['text']
            preview = text[:50] + '...' if len(text) > 50 else text
            lines.append(f"    内容: {preview}")
        elif 'html' in elem:
            lines.append(f"    内容: [HTML 表格]")

    return '\n'.join(lines)


def export_layout_json(elements: list, output_path: str) -> None:
    """
    导出版面分析结果为 JSON

    Args:
        elements: 版面元素列表
        output_path: 输出路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'element_count': len(elements),
            'elements': elements
        }, f, ensure_ascii=False, indent=2)
    print(f"JSON 已保存: {output_path}")


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

    # 分析版面
    elements = analyze_layout(str(image_path))

    # 可视化
    visualization = visualize_layout(elements)
    print(visualization)

    # 保存结果
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_file = output_path / f"{image_path.stem}_layout.json"
    export_layout_json(elements, str(json_file))

    txt_file = output_path / f"{image_path.stem}_layout.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(visualization)
    print(f"TXT 已保存: {txt_file}")


if __name__ == "__main__":
    main()
