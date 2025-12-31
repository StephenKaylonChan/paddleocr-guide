#!/usr/bin/env python3
"""
竖排文字识别示例 - 使用 PaddleOCR (PP-OCRv5)
Vertical Text Recognition Example

适用模型: PP-OCRv5
功能: 识别竖排/纵向排列的文字
API 版本: PaddleOCR 3.x

测试图片要求:
- 中文竖排书籍、古籍
- 日文竖排文档
- 竖排标语、招牌
"""

from paddleocr import PaddleOCR
from pathlib import Path


def recognize_vertical_text(image_path: str, output_dir: str = None):
    """
    识别竖排文字 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径（竖排文字）
        output_dir: 输出目录

    Returns:
        结果对象
    """
    # 初始化 PaddleOCR（优化竖排文字识别）
    ocr = PaddleOCR(
        lang='ch',
        use_doc_orientation_classify=True,   # 文档方向检测
        use_textline_orientation=True,       # 文本行方向检测
    )

    print(f"正在识别竖排文字: {image_path}")
    print("=" * 50)

    # 执行预测
    result = ocr.predict(image_path)

    for res in result:
        # 打印结果
        res.print()

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            res.save_to_json(save_path=str(output_path))
            res.save_to_img(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return result


def recognize_japanese_vertical(image_path: str) -> list:
    """
    识别日文竖排文字

    Args:
        image_path: 图片路径

    Returns:
        识别的文字列表
    """
    ocr = PaddleOCR(
        lang='japan',  # 日文模型
        use_textline_orientation=True
    )

    result = ocr.predict(image_path)

    texts = []
    for res in result:
        res_json = res.json
        if 'rec_texts' in res_json:
            texts.extend(res_json['rec_texts'])

    return texts


def recognize_traditional_chinese(image_path: str) -> list:
    """
    识别繁体中文竖排文字

    Args:
        image_path: 图片路径

    Returns:
        识别的文字列表
    """
    ocr = PaddleOCR(
        lang='chinese_cht',  # 繁体中文模型
        use_textline_orientation=True
    )

    result = ocr.predict(image_path)

    texts = []
    for res in result:
        res_json = res.json
        if 'rec_texts' in res_json:
            texts.extend(res_json['rec_texts'])

    return texts


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "vertical"

    print("=" * 60)
    print("PP-OCRv5 竖排文字识别示例")
    print("=" * 60)
    print()
    print("关键参数:")
    print("  - use_doc_orientation_classify=True  # 文档方向检测")
    print("  - use_textline_orientation=True      # 文本行方向检测")
    print()
    print("支持语言:")
    print("  - lang='ch'           # 简体中文（默认）")
    print("  - lang='chinese_cht'  # 繁体中文")
    print("  - lang='japan'        # 日文")
    print()
    print("测试图片要求:")
    print("  - 竖排书籍、古籍")
    print("  - 日文竖排文档")
    print("  - 竖排标语、招牌")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备竖排文字图片进行测试")
        return

    # 识别竖排文字
    result = recognize_vertical_text(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("识别完成!")


if __name__ == "__main__":
    main()
