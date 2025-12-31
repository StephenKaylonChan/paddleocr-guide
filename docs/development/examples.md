# 示例代码开发指南

本文档说明如何开发和维护示例代码。

---

## 示例结构

```
examples/
├── basic/                    # 基础示例（PP-OCRv5）
│   ├── 01_simple_ocr.py      # 单图 OCR
│   ├── 02_batch_ocr.py       # 批量处理
│   └── 03_multilingual.py    # 多语言
├── document/                 # 文档处理（PP-StructureV3）
│   ├── 01_pdf_to_markdown.py # PDF 转 Markdown
│   ├── 02_table_recognition.py # 表格识别
│   └── 03_layout_analysis.py # 版面分析
└── advanced/                 # 高级示例（待开发）
```

---

## 命名规范

- 文件名：`{序号}_{功能名}.py`，如 `01_simple_ocr.py`
- 序号两位数字，从 01 开始
- 功能名使用小写字母和下划线

---

## 代码规范

### 文件头模板

```python
#!/usr/bin/env python3
"""
{示例名称} - 使用 {模型名}
{English Name}

适用模型: {PP-OCRv5 | PP-StructureV3 | ...}
功能: {简要描述}
"""
```

### 必须包含

1. **docstring**: 中英文描述
2. **类型注解**: 函数参数和返回值
3. **main()**: 独立可运行的入口函数
4. **错误处理**: 检查文件是否存在

### 代码风格

- 遵循 PEP 8
- 使用 black 格式化（line-length=100）
- 使用 isort 排序导入

---

## 添加新示例

### 1. 确定分类

| 分类 | 模型 | 适用场景 |
|------|------|----------|
| basic/ | PP-OCRv5 | 简单文字识别 |
| document/ | PP-StructureV3 | 文档/表格/PDF |
| advanced/ | 混合 | 复杂场景 |

### 2. 创建文件

```bash
# 示例：添加新的 basic 示例
touch examples/basic/04_new_feature.py
```

### 3. 遵循模板

参考现有示例的结构，确保包含：
- 文件头 docstring
- 主要功能函数
- `main()` 入口
- `if __name__ == "__main__"` 块

### 4. 测试

```bash
python examples/basic/04_new_feature.py
```

### 5. 更新索引

更新 `examples/README.md` 添加新示例说明。

---

## 测试图片

测试图片放置在 `assets/test_images/` 目录。

示例代码默认使用 `assets/test_images/test.png`。

---

## 输出目录

所有示例输出保存到 `assets/outputs/`，由代码自动创建。
