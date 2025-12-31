#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR Guide CLI - 命令行工具

提供常用 OCR 功能的命令行接口，无需编写 Python 代码。

使用示例:
    # 识别单张图片
    paddleocr-guide scan image.png

    # 批量处理目录
    paddleocr-guide batch ./images/ -o ./results/

    # PDF 转 Markdown
    paddleocr-guide pdf document.pdf -o output.md

    # 指定语言
    paddleocr-guide scan image.png --lang en
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_ocr(lang: str = "ch"):
    """延迟加载 OCR 实例"""
    try:
        from paddleocr import PaddleOCR
        return PaddleOCR(lang=lang)
    except ImportError:
        click.echo("错误: PaddleOCR 未安装，请运行: pip install paddleocr", err=True)
        sys.exit(1)


@click.group()
@click.version_option(version="0.2.0", prog_name="paddleocr-guide")
def cli():
    """
    PaddleOCR Guide - 中文 OCR 命令行工具

    基于 PaddleOCR 3.x，支持图片识别、批量处理、PDF 转换等功能。
    """
    pass


@cli.command()
@click.argument("image", type=click.Path(exists=True))
@click.option("--lang", "-l", default="ch", help="语言代码 (默认: ch)")
@click.option("--output", "-o", type=click.Path(), help="输出文件路径 (可选)")
@click.option("--json", "as_json", is_flag=True, help="输出 JSON 格式")
def scan(image: str, lang: str, output: Optional[str], as_json: bool):
    """
    识别单张图片

    例:
        paddleocr-guide scan photo.png
        paddleocr-guide scan photo.png --lang en
        paddleocr-guide scan photo.png -o result.txt
        paddleocr-guide scan photo.png --json
    """
    import json as json_lib

    click.echo(f"正在识别: {image}")

    ocr = get_ocr(lang)
    result = ocr.predict(image)

    # 提取文本
    texts = []
    for res in result:
        data = res.json
        if "rec_texts" in data:
            for text, score in zip(data["rec_texts"], data["rec_scores"]):
                texts.append({"text": text, "confidence": float(score)})

    # 输出结果
    if as_json:
        output_content = json_lib.dumps(texts, ensure_ascii=False, indent=2)
    else:
        output_content = "\n".join(item["text"] for item in texts)

    if output:
        Path(output).write_text(output_content, encoding="utf-8")
        click.echo(f"结果已保存: {output}")
    else:
        click.echo("\n--- 识别结果 ---")
        click.echo(output_content)

    click.echo(f"\n共识别 {len(texts)} 条文本")


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--lang", "-l", default="ch", help="语言代码 (默认: ch)")
@click.option("--output", "-o", type=click.Path(), help="输出目录 (默认: 同目录下 ocr_results/)")
@click.option("--format", "-f", "fmt", type=click.Choice(["txt", "json"]), default="txt", help="输出格式")
def batch(directory: str, lang: str, output: Optional[str], fmt: str):
    """
    批量处理目录中的图片

    例:
        paddleocr-guide batch ./images/
        paddleocr-guide batch ./images/ -o ./results/
        paddleocr-guide batch ./images/ -f json
    """
    import json as json_lib

    dir_path = Path(directory)
    output_dir = Path(output) if output else dir_path / "ocr_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 查找图片
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
    images = [f for f in dir_path.iterdir() if f.suffix.lower() in extensions]

    if not images:
        click.echo(f"未找到图片文件: {directory}")
        return

    click.echo(f"找到 {len(images)} 张图片")

    ocr = get_ocr(lang)
    success_count = 0

    with click.progressbar(images, label="处理中") as bar:
        for img_path in bar:
            try:
                result = ocr.predict(str(img_path))

                # 提取文本
                texts = []
                for res in result:
                    data = res.json
                    if "rec_texts" in data:
                        for text, score in zip(data["rec_texts"], data["rec_scores"]):
                            texts.append({"text": text, "confidence": float(score)})

                # 保存结果
                ext = ".json" if fmt == "json" else ".txt"
                output_file = output_dir / f"{img_path.stem}{ext}"

                if fmt == "json":
                    content = json_lib.dumps(texts, ensure_ascii=False, indent=2)
                else:
                    content = "\n".join(item["text"] for item in texts)

                output_file.write_text(content, encoding="utf-8")
                success_count += 1

            except Exception as e:
                click.echo(f"\n处理失败 {img_path.name}: {e}", err=True)

    click.echo(f"\n完成: {success_count}/{len(images)} 成功")
    click.echo(f"结果保存在: {output_dir}")


@cli.command()
@click.argument("pdf_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
@click.option("--format", "-f", "fmt", type=click.Choice(["md", "txt", "json"]), default="md", help="输出格式")
def pdf(pdf_file: str, output: Optional[str], fmt: str):
    """
    PDF 文档转换 (转 Markdown/文本)

    例:
        paddleocr-guide pdf document.pdf
        paddleocr-guide pdf document.pdf -o result.md
        paddleocr-guide pdf document.pdf -f txt
    """
    import json as json_lib

    click.echo(f"正在处理 PDF: {pdf_file}")

    try:
        from paddleocr import PPStructureV3
        engine = PPStructureV3()
    except ImportError:
        click.echo("错误: PaddleOCR 未安装或版本不支持", err=True)
        sys.exit(1)

    result = engine.predict(pdf_file)

    # 确定输出文件
    pdf_path = Path(pdf_file)
    if output:
        output_path = Path(output)
    else:
        ext_map = {"md": ".md", "txt": ".txt", "json": ".json"}
        output_path = pdf_path.with_suffix(ext_map[fmt])

    # 保存结果
    for res in result:
        if fmt == "md":
            res.save_to_markdown(str(output_path.parent))
            # PPStructureV3 会自动命名，我们重命名
            auto_file = output_path.parent / f"{pdf_path.stem}.md"
            if auto_file.exists() and auto_file != output_path:
                auto_file.rename(output_path)
        elif fmt == "json":
            res.save_to_json(str(output_path.parent))
            auto_file = output_path.parent / f"{pdf_path.stem}.json"
            if auto_file.exists() and auto_file != output_path:
                auto_file.rename(output_path)
        else:  # txt
            # 提取纯文本
            data = res.json
            texts = []
            if "res" in data:
                for item in data["res"]:
                    if "text" in item:
                        texts.append(item["text"])
            output_path.write_text("\n".join(texts), encoding="utf-8")
        break  # 只处理第一个结果

    click.echo(f"完成: {output_path}")


@cli.command()
def langs():
    """
    显示支持的语言列表
    """
    from examples._common import SUPPORTED_LANGUAGES

    click.echo("支持的语言:\n")
    click.echo(f"{'代码':<15} {'语言'}")
    click.echo("-" * 40)
    for code, name in sorted(SUPPORTED_LANGUAGES.items()):
        click.echo(f"{code:<15} {name}")


@cli.command()
def info():
    """
    显示环境信息
    """
    import platform

    click.echo("环境信息:\n")

    # Python 版本
    click.echo(f"Python: {platform.python_version()}")
    click.echo(f"系统: {platform.system()} {platform.machine()}")

    # PaddleOCR 版本
    try:
        import paddleocr
        click.echo(f"PaddleOCR: {paddleocr.__version__}")
    except ImportError:
        click.echo("PaddleOCR: 未安装")

    # PaddlePaddle 版本
    try:
        import paddle
        click.echo(f"PaddlePaddle: {paddle.__version__}")
    except ImportError:
        click.echo("PaddlePaddle: 未安装")


def main():
    """入口函数"""
    cli()


if __name__ == "__main__":
    main()
