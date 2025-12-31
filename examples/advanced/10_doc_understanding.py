#!/usr/bin/env python3
"""
文档理解示例 - 使用 DocUnderstanding
Document Understanding Example

适用模型: DocUnderstanding (基于 VLM)
功能: 深度理解文档内容，回答关于文档的问题
API 版本: PaddleOCR 3.x

测试图片要求:
- 复杂文档（报告、论文、合同）
- 包含图表、表格的文档
- 需要理解上下文的文档

注意：需要 VLM 模型支持
"""

from paddleocr import DocUnderstanding
from pathlib import Path
import platform


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


def understand_document(image_path: str, questions: list = None, output_dir: str = None):
    """
    理解文档内容 (PaddleOCR 3.x)

    Args:
        image_path: 图片/PDF路径
        questions: 要问的问题列表
        output_dir: 输出目录

    Returns:
        理解结果
    """
    # 初始化文档理解产线
    doc_understand = DocUnderstanding(
        use_doc_orientation_classify=True,
        use_doc_unwarping=False
    )

    print(f"正在分析文档: {image_path}")
    print("=" * 50)

    # 执行文档理解
    output = doc_understand.predict(input=image_path)

    results = []
    for res in output:
        results.append(res)
        res.print()

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            res.save_to_json(save_path=str(output_path))
            res.save_to_markdown(save_path=str(output_path))

    if output_dir:
        print(f"\n结果已保存到: {output_dir}")

    return results


def ask_document(image_path: str, question: str) -> str:
    """
    询问文档内容

    Args:
        image_path: 图片路径
        question: 问题

    Returns:
        答案
    """
    doc_understand = DocUnderstanding()

    # 带问题的预测
    output = doc_understand.predict(
        input=image_path,
        prompt=question
    )

    for res in output:
        return res.json.get("answer", "")

    return ""


def batch_qa(image_path: str, questions: list) -> dict:
    """
    批量问答

    Args:
        image_path: 图片路径
        questions: 问题列表

    Returns:
        问答结果字典
    """
    doc_understand = DocUnderstanding()
    results = {}

    for question in questions:
        output = doc_understand.predict(
            input=image_path,
            prompt=question
        )
        for res in output:
            results[question] = res.json.get("answer", "未找到答案")
            break

    return results


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"
    output_dir = project_root / "assets" / "outputs" / "understanding"

    print("=" * 60)
    print("DocUnderstanding 文档理解示例")
    print("=" * 60)
    print()

    # 检查平台兼容性
    compatible, platform_info = check_platform_compatibility()
    print(f"当前平台: {platform_info}")
    print()

    if not compatible:
        print("⚠️  警告: 文档理解功能可能需要 VLM 模型支持")
        print("   VLM 模型不支持 macOS ARM")
        print()
        print("替代方案:")
        print("  - 使用 PP-StructureV3 进行文档解析")
        print("  - 使用 PP-ChatOCRv4Doc 进行信息抽取")
        print()

    print("功能说明:")
    print("  - 深度理解文档内容")
    print("  - 回答关于文档的问题")
    print("  - 提取关键信息")
    print()
    print("典型应用场景:")
    print("  - 合同审查：「这份合同的有效期是多久？」")
    print("  - 报告分析：「文档的主要结论是什么？」")
    print("  - 表格理解：「表格中的最大值是多少？」")
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("\n请准备需要理解的文档图片")
        return

    # 示例问题
    example_questions = [
        "这个文档的主题是什么？",
        "文档中提到了哪些关键信息？",
        "文档的日期是什么？"
    ]

    print("示例问题:")
    for q in example_questions:
        print(f"  - {q}")
    print()

    try:
        print("【执行文档理解】")
        results = understand_document(str(image_path), output_dir=str(output_dir))

        print("\n" + "=" * 60)
        print("分析完成!")
        print(f"共处理 {len(results)} 页")

    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("\n文档理解功能可能需要额外的依赖")
        print("请尝试: pip install paddleocr[all]")

    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print("\n可能原因:")
        print("  - VLM 模型不支持当前平台")
        print("  - 缺少必要的依赖")
        print("  - 内存不足")


if __name__ == "__main__":
    main()
