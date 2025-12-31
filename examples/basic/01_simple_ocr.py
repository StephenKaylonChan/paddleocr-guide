#!/usr/bin/env python3
"""
基础 OCR 示例 - 单张图片文字识别
Basic OCR Example - Single Image Text Recognition

适用模型: PP-OCRv5
支持系统: macOS / Linux / Windows
"""

from paddleocr import PaddleOCR
from pathlib import Path


def simple_ocr(image_path: str, lang: str = 'ch') -> list:
    """
    执行基础 OCR 识别

    Args:
        image_path: 图片路径
        lang: 语言代码 ('ch', 'en', 'japan', 'korean', etc.)

    Returns:
        识别结果列表
    """
    # 初始化 OCR 引擎
    # use_angle_cls: 启用方向分类（处理倾斜文字）
    # lang: 语言设置，'ch' 同时支持中英文
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang=lang,
        show_log=False  # 关闭详细日志
    )

    # 执行识别
    result = ocr.ocr(image_path, cls=True)

    return result[0] if result and result[0] else []


def format_result(ocr_result: list) -> None:
    """格式化输出识别结果"""
    if not ocr_result:
        print("未检测到文字")
        return

    print(f"共检测到 {len(ocr_result)} 行文字:\n")
    print("-" * 50)

    for idx, line in enumerate(ocr_result, 1):
        box, (text, confidence) = line[0], line[1]
        print(f"[{idx}] {text}")
        print(f"    置信度: {confidence:.2%}")
        # 只显示左上角和右下角坐标
        print(f"    位置: ({box[0][0]:.0f}, {box[0][1]:.0f}) - ({box[2][0]:.0f}, {box[2][1]:.0f})")
        print()


def save_result(ocr_result: list, output_path: str) -> None:
    """保存识别结果到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in ocr_result:
            text = line[1][0]
            confidence = line[1][1]
            f.write(f"{text}\t{confidence:.4f}\n")
    print(f"结果已保存到: {output_path}")


if __name__ == "__main__":
    # 示例：识别测试图片
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("请确保 assets/test_images/test.png 文件存在")
        exit(1)

    print(f"正在识别: {image_path}\n")

    result = simple_ocr(str(image_path))
    format_result(result)

    # 可选：保存结果
    # output_path = project_root / "assets" / "outputs" / "result.txt"
    # save_result(result, str(output_path))
