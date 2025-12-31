#!/usr/bin/env python3
"""
视觉语言模型示例 - 使用 PaddleOCR-VL
Vision-Language Model Example

适用模型: PaddleOCR-VL (0.9B)
功能: 109种语言支持、复杂文档理解、图表/公式/表格综合识别
API 版本: PaddleOCR 3.x

⚠️ 重要限制:
   PaddleOCR-VL 不支持 macOS ARM (M1/M2/M3/M4)
   仅支持: x86 架构 / NVIDIA GPU

测试图片要求:
- 复杂多语言文档
- 包含图表、公式、表格的综合文档
- 手写与印刷混合文档
"""

from pathlib import Path
import platform
import sys


def check_platform_compatibility():
    """检查平台兼容性"""
    machine = platform.machine().lower()
    system = platform.system().lower()

    if system == 'darwin' and machine in ['arm64', 'aarch64']:
        return False, "macOS ARM (M1/M2/M3/M4)"
    elif machine in ['arm64', 'aarch64']:
        return False, f"ARM64 ({system})"
    else:
        return True, f"{system} {machine}"


def recognize_with_vl(image_path: str, output_dir: str = None):
    """
    使用视觉语言模型识别 (PaddleOCR 3.x)

    Args:
        image_path: 图片路径
        output_dir: 输出目录

    Returns:
        结果对象列表
    """
    # 延迟导入，避免在不兼容平台上报错
    from paddleocr import PaddleOCRVL

    # 初始化 PaddleOCR-VL
    vl = PaddleOCRVL(
        use_doc_orientation_classify=True,
        use_doc_unwarping=False
    )

    print(f"正在使用 VL 模型识别: {image_path}")
    print("=" * 50)

    # 执行预测
    output = vl.predict(image_path)

    results = []
    for res in output:
        results.append(res)

        # 打印结果
        res.print()

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            res.save_to_markdown(save_path=str(output_path))
            res.save_to_json(save_path=str(output_path))
            res.save_to_img(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return results


def multilingual_ocr(image_path: str) -> str:
    """
    多语言文档识别

    Args:
        image_path: 图片路径

    Returns:
        Markdown 格式结果
    """
    from paddleocr import PaddleOCRVL

    vl = PaddleOCRVL()
    output = vl.predict(image_path)

    markdown_content = ""
    for res in output:
        markdown_content += res.markdown

    return markdown_content


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "vl"

    print("=" * 60)
    print("PaddleOCR-VL 视觉语言模型示例")
    print("=" * 60)
    print()

    # 检查平台兼容性
    compatible, platform_info = check_platform_compatibility()

    print(f"当前平台: {platform_info}")
    print()

    if not compatible:
        print("⚠️  警告: PaddleOCR-VL 不支持当前平台!")
        print()
        print("支持的平台:")
        print("  - x86_64 Linux (推荐)")
        print("  - x86_64 Windows")
        print("  - NVIDIA GPU (CUDA)")
        print()
        print("替代方案:")
        print("  - 使用 PP-OCRv5 进行基础 OCR")
        print("  - 使用 PP-StructureV3 进行文档解析")
        print("  - 在支持的服务器上部署 VL 模型")
        print()

        # 在不兼容平台上退出
        print("由于平台不兼容，示例无法运行。")
        return

    print("✅ 平台兼容，可以运行 VL 模型")
    print()
    print("模型特点:")
    print("  - 0.9B 参数，轻量级 VLM")
    print("  - 109 种语言支持")
    print("  - 图表、公式、表格综合理解")
    print("  - 手写与印刷混合识别")
    print()
    print("测试图片要求:")
    print("  - 复杂多语言文档")
    print("  - 图表/公式/表格综合文档")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备复杂文档图片进行测试")
        return

    # 使用 VL 模型识别
    try:
        results = recognize_with_vl(str(image_path), str(output_dir))

        print("\n" + "=" * 60)
        print("识别完成!")
        print(f"共处理 {len(results)} 页")

    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print("\n可能原因:")
        print("  - 模型文件未下载完成")
        print("  - 内存不足（VL 模型需要较大内存）")
        print("  - CUDA 环境问题")


if __name__ == "__main__":
    main()
