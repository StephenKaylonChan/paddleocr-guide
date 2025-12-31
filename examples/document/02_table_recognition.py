#!/usr/bin/env python3
"""
表格识别示例 - 使用 PP-StructureV3
Table Recognition Example

适用模型: PP-StructureV3
功能: 识别图片中的表格并导出为多种格式
"""

from paddleocr import PPStructure
from pathlib import Path
import json


def recognize_tables(image_path: str) -> list:
    """
    识别图片中的所有表格

    Args:
        image_path: 图片路径

    Returns:
        表格列表
    """
    # 初始化 PP-Structure
    structure = PPStructure(
        table=True,                      # 启用表格识别
        recovery=True,                   # 版面恢复
        return_ocr_result_in_table=True, # 返回表格内 OCR 结果
        show_log=False
    )

    # 识别
    result = structure(image_path)

    # 提取表格
    tables = []
    for idx, item in enumerate(result):
        if item.get('type') == 'table':
            tables.append({
                'index': idx,
                'bbox': item.get('bbox', []),
                'html': item.get('res', {}).get('html', ''),
                'cells': item.get('res', {}).get('cell_bbox', [])
            })

    return tables


def table_to_csv(table_html: str, output_path: str) -> bool:
    """
    将表格 HTML 转换为 CSV

    Args:
        table_html: 表格的 HTML 代码
        output_path: 输出 CSV 路径

    Returns:
        是否成功
    """
    try:
        import pandas as pd
        from io import StringIO

        # 使用 pandas 解析 HTML 表格
        dfs = pd.read_html(StringIO(table_html))
        if dfs:
            dfs[0].to_csv(output_path, index=False, encoding='utf-8')
            print(f"CSV 已保存: {output_path}")
            return True
    except ImportError:
        print("警告: 需要安装 pandas 才能导出 CSV")
        print("运行: pip install pandas")
    except Exception as e:
        print(f"转换失败: {e}")

    return False


def table_to_excel(table_html: str, output_path: str) -> bool:
    """
    将表格 HTML 转换为 Excel

    Args:
        table_html: 表格的 HTML 代码
        output_path: 输出 Excel 路径

    Returns:
        是否成功
    """
    try:
        import pandas as pd
        from io import StringIO

        dfs = pd.read_html(StringIO(table_html))
        if dfs:
            dfs[0].to_excel(output_path, index=False, engine='openpyxl')
            print(f"Excel 已保存: {output_path}")
            return True
    except ImportError:
        print("警告: 需要安装 pandas 和 openpyxl 才能导出 Excel")
        print("运行: pip install pandas openpyxl")
    except Exception as e:
        print(f"转换失败: {e}")

    return False


def process_table_image(image_path: str, output_dir: str = None) -> dict:
    """
    处理包含表格的图片

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        处理结果
    """
    print(f"处理图片: {image_path}")

    # 识别表格
    tables = recognize_tables(image_path)

    print(f"检测到 {len(tables)} 个表格")

    result = {
        'image': str(image_path),
        'table_count': len(tables),
        'tables': []
    }

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        stem = Path(image_path).stem

    for idx, table in enumerate(tables):
        print(f"\n--- 表格 {idx + 1} ---")

        table_info = {
            'index': idx,
            'bbox': table['bbox'],
            'html': table['html'][:200] + '...' if len(table['html']) > 200 else table['html']
        }

        if output_dir:
            # 保存 HTML
            html_file = output_path / f"{stem}_table_{idx + 1}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        table {{ border-collapse: collapse; margin: 20px; }}
        td, th {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>表格 {idx + 1}</h2>
    {table['html']}
</body>
</html>
""")
            print(f"HTML 已保存: {html_file}")

            # 保存 CSV
            csv_file = output_path / f"{stem}_table_{idx + 1}.csv"
            table_to_csv(table['html'], str(csv_file))

        result['tables'].append(table_info)

    # 保存汇总 JSON
    if output_dir:
        json_file = output_path / f"{stem}_tables.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n汇总 JSON 已保存: {json_file}")

    return result


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
    print(f"共识别 {result['table_count']} 个表格")


if __name__ == "__main__":
    main()
