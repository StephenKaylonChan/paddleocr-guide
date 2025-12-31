#!/usr/bin/env python3
"""
多语言 OCR 示例 - 识别不同语言的文字
Multilingual OCR Example

适用模型: PP-OCRv5
支持语言: 80+ 种语言
"""

from paddleocr import PaddleOCR
from pathlib import Path


# 支持的语言列表（常用）
SUPPORTED_LANGUAGES = {
    'ch': '中文（简体+繁体+英文）',
    'en': '英文',
    'korean': '韩文',
    'japan': '日文',
    'chinese_cht': '繁体中文',
    'ta': '泰米尔语',
    'te': '泰卢固语',
    'ka': '卡纳达语',
    'latin': '拉丁语系',
    'arabic': '阿拉伯语',
    'cyrillic': '西里尔语系（俄语等）',
    'devanagari': '天城文（印地语等）',
    'french': '法语',
    'german': '德语',
    'it': '意大利语',
    'es': '西班牙语',
    'pt': '葡萄牙语',
}


def create_ocr_engine(lang: str = 'ch') -> PaddleOCR:
    """
    创建指定语言的 OCR 引擎

    Args:
        lang: 语言代码

    Returns:
        PaddleOCR 实例
    """
    return PaddleOCR(
        use_angle_cls=True,
        lang=lang,
        show_log=False
    )


def recognize_with_language(image_path: str, lang: str = 'ch') -> list:
    """
    使用指定语言识别图片

    Args:
        image_path: 图片路径
        lang: 语言代码

    Returns:
        识别结果
    """
    ocr = create_ocr_engine(lang)
    result = ocr.ocr(image_path, cls=True)

    texts = []
    if result and result[0]:
        for line in result[0]:
            texts.append({
                'text': line[1][0],
                'confidence': line[1][1]
            })

    return texts


def auto_detect_language(image_path: str, languages: list = None) -> dict:
    """
    尝试多种语言识别，返回置信度最高的结果

    Args:
        image_path: 图片路径
        languages: 要尝试的语言列表

    Returns:
        最佳识别结果
    """
    if languages is None:
        languages = ['ch', 'en', 'japan', 'korean']

    best_result = None
    best_avg_confidence = 0

    for lang in languages:
        print(f"  尝试语言: {SUPPORTED_LANGUAGES.get(lang, lang)}")

        try:
            texts = recognize_with_language(image_path, lang)

            if texts:
                avg_confidence = sum(t['confidence'] for t in texts) / len(texts)
                print(f"    平均置信度: {avg_confidence:.2%}")

                if avg_confidence > best_avg_confidence:
                    best_avg_confidence = avg_confidence
                    best_result = {
                        'language': lang,
                        'language_name': SUPPORTED_LANGUAGES.get(lang, lang),
                        'avg_confidence': avg_confidence,
                        'texts': texts
                    }
        except Exception as e:
            print(f"    错误: {e}")

    return best_result


def print_supported_languages():
    """打印支持的语言列表"""
    print("支持的语言列表:")
    print("-" * 40)
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"  {code:15} - {name}")
    print("-" * 40)
    print("完整语言列表请参考 PaddleOCR 官方文档")


def main():
    """主函数 - 演示多语言识别"""
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / "assets" / "test_images" / "test.png"

    print("=" * 50)
    print("PaddleOCR 多语言识别示例")
    print("=" * 50)
    print()

    # 打印支持的语言
    print_supported_languages()
    print()

    if not image_path.exists():
        print(f"测试图片不存在: {image_path}")
        print("请准备测试图片后运行")
        return

    # 示例 1: 中文识别
    print("\n【示例 1】中文识别")
    print("-" * 30)
    texts = recognize_with_language(str(image_path), 'ch')
    for t in texts[:5]:  # 只显示前 5 行
        print(f"  {t['text']} ({t['confidence']:.2%})")
    if len(texts) > 5:
        print(f"  ... 共 {len(texts)} 行")

    # 示例 2: 自动检测语言
    print("\n【示例 2】自动检测语言")
    print("-" * 30)
    result = auto_detect_language(str(image_path))
    if result:
        print(f"\n最佳匹配语言: {result['language_name']}")
        print(f"平均置信度: {result['avg_confidence']:.2%}")

    # 示例 3: 中英混合识别
    print("\n【示例 3】中英混合识别说明")
    print("-" * 30)
    print("lang='ch' 默认支持中英文混合识别")
    print("无需单独处理英文内容")


if __name__ == "__main__":
    main()
