#!/usr/bin/env python3
"""
手写文字识别示例 - 使用 PaddleOCR (PP-OCRv5)
Handwriting Recognition Example

适用模型: PP-OCRv5
功能: 识别手写文字，包括潦草字迹和倾斜文本
API 版本: PaddleOCR 3.x

测试图片要求:
- 手写笔记、便签
- 手写表格、表单
- 签名、批注
"""

from paddleocr import PaddleOCR
from pathlib import Path


def recognize_handwriting(image_path: str, output_dir: str = None):
    """
    识别手写文字 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径（手写文档）
        output_dir: 输出目录

    Returns:
        结果对象
    """
    # 初始化 PaddleOCR（优化手写识别）
    ocr = PaddleOCR(
        lang='ch',
        use_textline_orientation=True,   # 处理倾斜手写文字
        use_doc_orientation_classify=True,  # 文档方向检测
        text_det_thresh=0.3,             # 降低阈值，检测更多笔迹
        text_det_box_thresh=0.5,         # 降低框阈值
        text_rec_score_thresh=0.3        # 降低识别阈值
    )

    print(f"正在识别手写文字: {image_path}")
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


def extract_handwriting_text(image_path: str) -> list:
    """
    提取手写文字内容

    Args:
        image_path: 图片路径

    Returns:
        识别的文字列表
    """
    ocr = PaddleOCR(
        lang='ch',
        use_textline_orientation=True,
        text_det_thresh=0.3
    )

    result = ocr.predict(image_path)

    texts = []
    for res in result:
        res_json = res.json
        if 'rec_texts' in res_json:
            texts.extend(res_json['rec_texts'])

    return texts


def recognize_with_confidence_filter(image_path: str, min_confidence: float = 0.5) -> list:
    """
    识别手写文字并按置信度过滤

    Args:
        image_path: 图片路径
        min_confidence: 最低置信度阈值

    Returns:
        高置信度的识别结果
    """
    ocr = PaddleOCR(
        lang='ch',
        use_textline_orientation=True,
        text_det_thresh=0.3
    )

    result = ocr.predict(image_path)

    filtered_results = []
    for res in result:
        res_json = res.json
        if 'rec_texts' in res_json and 'rec_scores' in res_json:
            for text, score in zip(res_json['rec_texts'], res_json['rec_scores']):
                if score >= min_confidence:
                    filtered_results.append({
                        'text': text,
                        'confidence': score
                    })

    return filtered_results


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "handwriting"

    print("=" * 60)
    print("PP-OCRv5 手写文字识别示例")
    print("=" * 60)
    print()
    print("优化参数说明:")
    print("  - use_textline_orientation=True  # 处理倾斜文字")
    print("  - text_det_thresh=0.3            # 降低检测阈值")
    print("  - text_rec_score_thresh=0.3      # 降低识别阈值")
    print()
    print("测试图片要求:")
    print("  - 手写笔记、便签、批注")
    print("  - 尽量清晰，对比度高")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备手写文档图片进行测试")
        return

    # 识别手写文字
    result = recognize_handwriting(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("识别完成!")

    # 按置信度过滤
    print("\n高置信度结果 (>= 50%):")
    filtered = recognize_with_confidence_filter(str(image_path), 0.5)
    for item in filtered[:10]:  # 只显示前10个
        print(f"  {item['text']} ({item['confidence']:.1%})")
    if len(filtered) > 10:
        print(f"  ... 共 {len(filtered)} 条")


if __name__ == "__main__":
    main()
