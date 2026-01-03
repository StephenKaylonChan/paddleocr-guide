# 快速入门教程

> 5 分钟上手 PaddleOCR - 从安装到实际应用

本教程将带你快速掌握 PaddleOCR 的核心功能，适合完全新手。

---

## 一、最简单的例子（1 分钟）

### 1. 安装 PaddleOCR

```bash
pip install paddleocr
```

**macOS 用户注意**: 首次运行会自动下载模型（约 10MB），请确保网络畅通。

### 2. 第一行代码

创建文件 `test_ocr.py`：

```python
from paddleocr import PaddleOCR

# 初始化 OCR（macOS 必须添加这 3 个参数）
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

# 识别图片
result = ocr.predict('test.png')

# 打印结果
for res in result:
    res.print()
```

### 3. 运行

```bash
python test_ocr.py
```

**输出示例**:
```
检测到的文本：Hello, PaddleOCR！
置信度：0.9876
```

🎉 **恭喜！** 你已经完成了第一次 OCR 识别！

---

## 二、三个核心场景（3 分钟）

### 场景 1：单张图片识别

**需求**: 识别一张图片中的文字

```python
from paddleocr import PaddleOCR

# 初始化（macOS 优化配置）
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

# 识别
result = ocr.predict('invoice.png')

# 提取纯文本
for res in result:
    data = res.json
    if 'rec_texts' in data:
        texts = data['rec_texts']
        print('\n'.join(texts))
```

**适用场景**: 发票识别、名片识别、截图识别

---

### 场景 2：批量处理文件夹

**需求**: 处理一个文件夹中的所有图片

```python
from paddleocr import PaddleOCR
from pathlib import Path

# 初始化
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

# 遍历文件夹
image_dir = Path('images/')
for img_path in image_dir.glob('*.png'):
    print(f'\n处理: {img_path.name}')

    result = ocr.predict(str(img_path))

    # 保存结果到 txt
    output_file = img_path.with_suffix('.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for res in result:
            data = res.json
            if 'rec_texts' in data:
                f.write('\n'.join(data['rec_texts']))

    print(f'✓ 已保存到: {output_file}')
```

**适用场景**: 批量文档处理、归档扫描件、数据提取

---

### 场景 3：PDF 转 Markdown

**需求**: 将扫描版 PDF 转为可编辑的 Markdown

```python
from paddleocr import PPStructureV3
from pathlib import Path

# 初始化（文档分析专用）
engine = PPStructureV3(lang='ch')

# 识别 PDF
result = engine.predict('document.pdf')

# 保存为 Markdown
output_path = Path('output.md')
for res in result:
    res.save_to_markdown(str(output_path))

print(f'✓ PDF 已转换为: {output_path}')
```

**适用场景**: 书籍转换、学术论文、历史文档数字化

**输出示例** (`output.md`):
```markdown
# 第一章 标题

这是正文内容...

| 表头1 | 表头2 |
|------|------|
| 数据1 | 数据2 |
```

---

## 三、常见问题快速解答

### Q1: 如何提高识别准确率？

**方法 1**: 使用更大的 Server 模型（默认是轻量级模型）

```python
ocr = PaddleOCR(
    lang='ch',
    det_model_dir='ch_PP_OCRv5_server_det',  # Server 模型
    rec_model_dir='ch_PP_OCRv5_server_rec',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
```

**方法 2**: 预处理图片（提高清晰度）

```python
from PIL import Image, ImageEnhance

# 打开图片
img = Image.open('test.png')

# 增强锐度
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(2.0)

# 保存
img.save('test_enhanced.png')

# 识别增强后的图片
result = ocr.predict('test_enhanced.png')
```

**参考**: 详见 [性能优化专题](performance.md#准确率优化)

---

### Q2: 内存占用太高怎么办？

**问题**: macOS 系统 OCR 时内存占用 40GB+，系统卡死

**解决方案**: **必须**添加这 3 个参数（已在上面示例中包含）

```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,  # 禁用文档方向分类
    use_doc_unwarping=False,             # 禁用文档矫正
    use_textline_orientation=False,      # 禁用文本行方向
)
```

**效果**: 内存从 40GB 降至 **0.7GB**（节省 98.2%）

**大图片处理**: 如果图片尺寸超过 2000px，建议先缩小：

```python
from examples._common import resize_image_for_ocr

# 自动缩小到 1200px（保持宽高比）
resized_path = resize_image_for_ocr('large_image.png', max_size=1200)

# 识别缩小后的图片
result = ocr.predict(resized_path)
```

**参考**: 详见 [故障排查 - Q5 内存占用过高](troubleshooting.md#q5-内存占用过高)

---

### Q3: 如何识别其他语言？

支持 **80+ 种语言**，只需修改 `lang` 参数：

```python
# 英文
ocr_en = PaddleOCR(lang='en', ...)

# 日文
ocr_ja = PaddleOCR(lang='japan', ...)

# 韩文
ocr_ko = PaddleOCR(lang='korean', ...)

# 法文
ocr_fr = PaddleOCR(lang='french', ...)
```

**查看所有支持的语言**:

```bash
paddleocr-guide langs
```

或使用代码：

```python
from examples._common import SUPPORTED_LANGUAGES

print(f"支持 {len(SUPPORTED_LANGUAGES)} 种语言:")
for lang in SUPPORTED_LANGUAGES[:10]:
    print(f"  - {lang}")
```

**参考**: 详见 [API 参考 - 语言列表](api_reference.md#支持的语言)

---

### Q4: 如何保存识别结果为 JSON？

```python
result = ocr.predict('test.png')

# 方法 1: 使用内置方法
for res in result:
    res.save_to_json('output.json')

# 方法 2: 手动提取
import json

output_data = []
for res in result:
    data = res.json
    output_data.append({
        'texts': data.get('rec_texts', []),
        'scores': data.get('rec_scores', []),
        'boxes': data.get('det_boxes', []),
    })

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
```

**输出示例** (`output.json`):
```json
[
  {
    "texts": ["Hello", "World"],
    "scores": [0.9876, 0.9654],
    "boxes": [[10, 10, 100, 50], [10, 60, 120, 100]]
  }
]
```

---

### Q5: 如何只识别图片中的某个区域？

```python
from PIL import Image

# 裁剪感兴趣区域（ROI）
img = Image.open('test.png')
roi = img.crop((100, 100, 500, 300))  # (left, top, right, bottom)
roi.save('roi.png')

# 识别裁剪区域
result = ocr.predict('roi.png')
```

**适用场景**: 身份证号提取、发票金额识别、固定位置信息

---

## 四、下一步学习

### 📚 推荐学习路径

**新手**:
1. ✅ **你已完成**: 快速入门教程（当前页面）
2. → 查看完整示例: [examples/](../../examples/)
   - 从 `basic/01_simple_ocr.py` 开始
3. → 阅读 [API 参考](api_reference.md) 了解所有参数

**进阶**:
4. → [性能优化专题](performance.md) - 内存、速度、准确率优化
5. → [实际案例集](case_studies.md) - 发票、身份证、PDF 转换
6. → [最佳实践](best_practices.md) - 代码规范和设计模式

**部署**:
7. → [部署指南](deployment.md) - Docker、生产环境配置
8. → [故障排查](troubleshooting.md) - 常见问题解决

---

### 💻 CLI 命令行工具

如果你不想写代码，可以直接使用命令行工具：

```bash
# 安装项目
pip install -e .

# 识别单张图片
paddleocr-guide scan test.png

# 批量处理文件夹
paddleocr-guide batch images/ --output results/

# PDF 转 Markdown
paddleocr-guide pdf document.pdf --output output.md

# 查看支持的语言
paddleocr-guide langs
```

**参考**: [CLI 命令行工具](../../README.md#cli-命令行工具)

---

### 🔧 使用公共模块（推荐）

项目提供了公共模块 `examples._common`，简化常见操作：

```python
from examples._common import quick_ocr

# 一行代码完成识别（自动处理资源）
result = quick_ocr('test.png', lang='ch')
```

**其他工具函数**:
```python
from examples._common import (
    OCRContextManager,      # 上下文管理器
    resize_image_for_ocr,   # 图片预处理
    find_images,            # 查找图片文件
    save_json,              # 保存 JSON
    extract_text_only,      # 提取纯文本
)

# 批量查找图片
images = find_images('images/', extensions=['.png', '.jpg'])

# 预处理大图片
resized = resize_image_for_ocr('large.png', max_size=1200)

# 使用上下文管理器（自动释放资源）
with OCRContextManager(lang='ch') as ocr:
    result = ocr.predict('test.png')
```

**参考**: [examples/_common/](../../examples/_common/)

---

### 📖 完整示例代码

项目包含 **16 个完整示例**，涵盖所有常见场景：

| 类别 | 示例 | 说明 |
|------|------|------|
| **基础** | [01_simple_ocr.py](../../examples/basic/01_simple_ocr.py) | 简单 OCR |
| | [02_batch_ocr.py](../../examples/basic/02_batch_ocr.py) | 批量处理 |
| | [03_multilingual.py](../../examples/basic/03_multilingual.py) | 多语言 |
| **文档** | [01_pdf_to_markdown.py](../../examples/document/01_pdf_to_markdown.py) | PDF 转 Markdown |
| | [02_table_recognition.py](../../examples/document/02_table_recognition.py) | 表格识别 |
| | [03_layout_analysis.py](../../examples/document/03_layout_analysis.py) | 版面分析 |
| **高级** | [04_chatocr_extraction.py](../../examples/advanced/04_chatocr_extraction.py) | 智能信息抽取 |
| | [05_handwriting_ocr.py](../../examples/advanced/05_handwriting_ocr.py) | 手写文字 |
| | [更多...](../../examples/advanced/) | 印章、公式、图表等 |

**查看所有示例**: [examples/README.md](../../examples/README.md)

---

## 五、需要帮助？

- 💬 **问题反馈**: [GitHub Issues](https://github.com/stephenkaylonchan/paddleocr-guide/issues)
- 📚 **完整文档**: [docs/zh/](README.md)
- 🎯 **PaddleOCR 官方**: [https://paddleocr.ai/](https://paddleocr.ai/)

---

## 附录：常用代码片段

### A. 最简配置（复制即用）

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

result = ocr.predict('test.png')
for res in result:
    res.print()
```

### B. 提取纯文本

```python
texts = []
for res in result:
    data = res.json
    if 'rec_texts' in data:
        texts.extend(data['rec_texts'])

print('\n'.join(texts))
```

### C. 批量处理模板

```python
from pathlib import Path

image_dir = Path('images/')
for img_path in image_dir.glob('*.png'):
    result = ocr.predict(str(img_path))
    # 处理 result...
```

### D. 错误处理

```python
try:
    result = ocr.predict('test.png')
except Exception as e:
    print(f'识别失败: {e}')
    # 处理错误...
```

---

**上次更新**: 2026-01-03
**版本**: v0.3.0
