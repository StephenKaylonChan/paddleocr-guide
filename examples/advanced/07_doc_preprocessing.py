#!/usr/bin/env python3
"""
文档预处理示例 - 使用 PP-StructureV3
Document Preprocessing Example

适用模型: PP-StructureV3
功能: 文档方向检测与矫正、弯曲文档矫正
API 版本: PaddleOCR 3.x

测试图片要求:
- 拍摄角度倾斜的文档
- 弯曲或卷曲的纸张照片
- 手机拍摄的文档（透视变形）
"""

from paddleocr import PPStructureV3
from pathlib import Path


def preprocess_and_ocr(image_path: str, output_dir: str = None):
    """
    文档预处理后进行 OCR (PaddleOCR 3.x)

    Args:
        image_path: 图片路径（需要预处理的文档）
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    # 初始化 PP-StructureV3（启用全部预处理）
    pipeline = PPStructureV3(
        use_doc_orientation_classify=True,  # 文档方向检测与矫正
        use_doc_unwarping=True,             # 弯曲文档矫正
        use_table_recognition=True,
        use_formula_recognition=False,
        use_seal_recognition=False
    )

    print(f"正在预处理并识别: {image_path}")
    print("=" * 50)
    print("预处理步骤:")
    print("  1. 文档方向检测与矫正")
    print("  2. 弯曲文档矫正")
    print("  3. OCR 识别")
    print()

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

            # 保存预处理后的图片和结果
            res.save_to_img(save_path=str(output_path))
            res.save_to_json(save_path=str(output_path))
            res.save_to_markdown(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")
        print("包含预处理后的图片")

    return results


def orientation_only(image_path: str, output_dir: str = None):
    """
    仅进行文档方向矫正

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    pipeline = PPStructureV3(
        use_doc_orientation_classify=True,  # 仅方向矫正
        use_doc_unwarping=False,
        use_table_recognition=False,
        use_formula_recognition=False
    )

    print("执行方向矫正...")
    output = pipeline.predict(input=image_path)

    for res in output:
        res.print()
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            res.save_to_img(save_path=str(output_path))

    return list(output)


def unwarping_only(image_path: str, output_dir: str = None):
    """
    仅进行弯曲矫正

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    pipeline = PPStructureV3(
        use_doc_orientation_classify=False,
        use_doc_unwarping=True,             # 仅弯曲矫正
        use_table_recognition=False,
        use_formula_recognition=False
    )

    print("执行弯曲矫正...")
    output = pipeline.predict(input=image_path)

    for res in output:
        res.print()
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            res.save_to_img(save_path=str(output_path))

    return list(output)


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "preprocessing"

    print("=" * 60)
    print("PP-StructureV3 文档预处理示例")
    print("=" * 60)
    print()
    print("预处理功能:")
    print("  1. use_doc_orientation_classify  # 文档方向检测与矫正")
    print("     - 检测文档是否旋转（0°/90°/180°/270°）")
    print("     - 自动矫正到正确方向")
    print()
    print("  2. use_doc_unwarping             # 弯曲文档矫正")
    print("     - 矫正弯曲、卷曲的文档")
    print("     - 修复透视变形")
    print()
    print("测试图片要求:")
    print("  - 倾斜拍摄的文档")
    print("  - 弯曲或卷曲的纸张")
    print("  - 手机拍摄的文档")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备需要预处理的文档图片")
        return

    # 完整预处理
    print("【完整预处理模式】")
    results = preprocess_and_ocr(str(image_path), str(output_dir))

    print("\n" + "=" * 60)
    print("预处理完成!")
    print(f"共处理 {len(results)} 页")


if __name__ == "__main__":
    main()
