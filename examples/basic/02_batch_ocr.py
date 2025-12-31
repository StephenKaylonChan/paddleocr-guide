#!/usr/bin/env python3
"""
批量 OCR 示例 - 处理多张图片
Batch OCR Example - Process Multiple Images

适用模型: PP-OCRv5
支持系统: macOS / Linux / Windows
API 版本: PaddleOCR 3.x
"""

from paddleocr import PaddleOCR
from pathlib import Path
import json
from datetime import datetime


class BatchOCR:
    """批量 OCR 处理器 (PaddleOCR 3.x)"""

    def __init__(self, lang: str = 'ch'):
        """
        初始化批量处理器

        Args:
            lang: 语言代码
        """
        # 只初始化一次模型，提高效率
        self.ocr = PaddleOCR(
            lang=lang,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )

    def process_image(self, image_path: str) -> dict:
        """
        处理单张图片

        Args:
            image_path: 图片路径

        Returns:
            识别结果字典
        """
        result = self.ocr.predict(image_path)

        texts = []
        for res in result:
            # 获取 JSON 格式的结果
            res_json = res.json
            if 'rec_texts' in res_json and 'rec_scores' in res_json:
                for text, score in zip(res_json['rec_texts'], res_json['rec_scores']):
                    texts.append({
                        'text': text,
                        'confidence': float(score)
                    })

        return {
            'file': Path(image_path).name,
            'path': str(image_path),
            'text_count': len(texts),
            'texts': texts
        }

    def process_directory(self, input_dir: str, output_dir: str = None) -> list:
        """
        批量处理目录中的所有图片

        Args:
            input_dir: 输入目录
            output_dir: 输出目录（可选）

        Returns:
            所有图片的识别结果
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"目录不存在: {input_dir}")

        # 支持的图片格式
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}

        # 获取所有图片文件
        image_files = [
            f for f in input_path.iterdir()
            if f.suffix.lower() in image_extensions
        ]

        if not image_files:
            print(f"目录中没有找到图片文件: {input_dir}")
            return []

        print(f"找到 {len(image_files)} 张图片，开始处理...\n")

        results = []
        for i, img_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] 处理: {img_path.name}")

            try:
                result = self.process_image(str(img_path))
                results.append(result)
                print(f"    检测到 {result['text_count']} 行文字")

                # 保存单个文件的结果
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)

                    txt_file = output_path / f"{img_path.stem}.txt"
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        for item in result['texts']:
                            f.write(f"{item['text']}\n")

            except Exception as e:
                print(f"    错误: {e}")
                results.append({
                    'file': img_path.name,
                    'path': str(img_path),
                    'error': str(e)
                })

        # 保存汇总结果
        if output_dir:
            summary_file = Path(output_dir) / "summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'processed_at': datetime.now().isoformat(),
                    'total_images': len(image_files),
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n汇总结果已保存: {summary_file}")

        return results


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / "assets" / "test_images"
    output_dir = project_root / "assets" / "outputs"

    # 创建批量处理器
    processor = BatchOCR(lang='ch')

    # 处理目录
    results = processor.process_directory(
        str(input_dir),
        str(output_dir)
    )

    # 打印统计信息
    print("\n" + "=" * 50)
    print("处理完成统计:")
    print(f"  总图片数: {len(results)}")
    success_count = sum(1 for r in results if 'error' not in r)
    print(f"  成功处理: {success_count}")
    print(f"  失败数量: {len(results) - success_count}")

    total_texts = sum(r.get('text_count', 0) for r in results)
    print(f"  总文字行数: {total_texts}")


if __name__ == "__main__":
    main()
