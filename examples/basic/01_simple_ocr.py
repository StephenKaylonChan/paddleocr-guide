#!/usr/bin/env python3
"""
基础 OCR 示例 - 单张图片文字识别
Basic OCR Example - Single Image Text Recognition

适用模型: PP-OCRv5
支持系统: macOS / Linux / Windows
API 版本: PaddleOCR 3.x
"""

from paddleocr import PaddleOCR
from pathlib import Path


def simple_ocr(image_path: str, lang: str = 'ch'):
    """
    执行基础 OCR 识别 (PaddleOCR 3.x API)

    Args:
        image_path: 图片路径
        lang: 语言代码 ('ch', 'en', 'japan', 'korean', etc.)

    Returns:
        结果对象迭代器
    """
    # 初始化 OCR 引擎
    # use_doc_orientation_classify: 文档方向分类
    # use_doc_unwarping: 文档弯曲矫正
    # use_textline_orientation: 文本行方向分类
    ocr = PaddleOCR(
        lang=lang,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False
    )

    # 执行识别 (PaddleOCR 3.x 使用 predict 方法)
    result = ocr.predict(image_path)

    return result


def format_result(result) -> None:
    """格式化输出识别结果"""
    for res in result:
        # 使用内置 print 方法输出
        res.print()


def save_result_json(result, output_dir: str) -> None:
    """保存识别结果为 JSON"""
    for res in result:
        res.save_to_json(output_dir)
    print(f"JSON 结果已保存到: {output_dir}")


def save_result_img(result, output_dir: str) -> None:
    """保存可视化结果图片"""
    for res in result:
        res.save_to_img(output_dir)
    print(f"可视化图片已保存到: {output_dir}")


if __name__ == "__main__":
    # 示例：识别测试图片
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs"

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("请确保 assets/test_images/test.png 文件存在")
        exit(1)

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"正在识别: {image_path}\n")

    # 执行 OCR
    result = simple_ocr(str(image_path))

    # 输出结果
    format_result(result)

    # 可选：保存结果
    # save_result_json(result, str(output_dir))
    # save_result_img(result, str(output_dir))
