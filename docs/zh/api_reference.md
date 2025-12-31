# PaddleOCR 3.x API 完整参考

> 基于源码分析的完整 API 文档

---

## 目录

- [Pipeline 总览](#pipeline-总览)
- [PaddleOCR - 通用 OCR](#paddleocr---通用-ocr)
- [PPStructureV3 - 文档解析](#ppstructurev3---文档解析)
- [PPChatOCRv4Doc - 智能抽取](#ppchatocrv4doc---智能抽取)
- [PaddleOCRVL - 视觉语言模型](#paddleocrvl---视觉语言模型)
- [DocPreprocessor - 文档预处理](#docpreprocessor---文档预处理)
- [PPDocTranslation - 文档翻译](#ppdoctranslation---文档翻译)
- [SealRecognition - 印章识别](#sealrecognition---印章识别)
- [通用参数说明](#通用参数说明)
- [支持的语言列表](#支持的语言列表)

---

## Pipeline 总览

PaddleOCR 3.x 提供 10 个高级 Pipeline：

| Pipeline | 功能 | macOS ARM | 适用场景 |
|----------|------|-----------|----------|
| `PaddleOCR` | 通用 OCR | ✅ | 图片文字识别 |
| `PPStructureV3` | 文档解析 | ✅ | PDF/表格/版面分析 |
| `PPChatOCRv4Doc` | 智能抽取 | ✅ | 票据/证件信息提取 |
| `PaddleOCRVL` | 视觉语言 | ❌ | 复杂文档理解 |
| `DocPreprocessor` | 文档预处理 | ✅ | 方向/弯曲矫正 |
| `PPDocTranslation` | 文档翻译 | ✅* | 多语言文档翻译 |
| `SealRecognition` | 印章识别 | ✅ | 公章/印章提取 |
| `FormulaRecognitionPipeline` | 公式识别 | ✅ | 数学公式转 LaTeX |
| `TableRecognitionPipelineV2` | 表格识别 | ✅ | 表格结构识别 |
| `DocUnderstanding` | 文档理解 | ❌ | 文档问答 |

> *PPDocTranslation 需要配置 LLM API

---

## PaddleOCR - 通用 OCR

基础 OCR，识别图片中的文字。

### 导入

```python
from paddleocr import PaddleOCR
```

### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lang` | str | `"ch"` | 语言，见[支持的语言列表](#支持的语言列表) |
| `ocr_version` | str | `"PP-OCRv5"` | OCR 版本 (PP-OCRv3/v4/v5) |
| `use_doc_orientation_classify` | bool | `False` | 启用文档方向分类 |
| `use_doc_unwarping` | bool | `False` | 启用弯曲矫正 |
| `use_textline_orientation` | bool | `False` | 启用文本行方向分类 |

### 检测参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `text_det_limit_side_len` | int | 检测图像边长限制 |
| `text_det_limit_type` | str | 边长限制类型 (`min`/`max`) |
| `text_det_thresh` | float | 检测像素阈值 (默认 0.3) |
| `text_det_box_thresh` | float | 检测框阈值 (默认 0.6) |
| `text_det_unclip_ratio` | float | 文本区域扩展系数 (默认 1.5) |
| `text_det_input_shape` | tuple | 检测模型输入形状 (C, H, W) |

### 识别参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `text_rec_score_thresh` | float | 识别分数阈值 |
| `text_recognition_batch_size` | int | 识别批次大小 |
| `return_word_box` | bool | 返回单词级别坐标 |
| `text_rec_input_shape` | tuple | 识别模型输入形状 |

### 使用示例

```python
from paddleocr import PaddleOCR

# 基础使用
ocr = PaddleOCR(lang='ch')
result = ocr.predict('image.png')

for res in result:
    res.print()

# 高级配置
ocr = PaddleOCR(
    lang='ch',
    ocr_version='PP-OCRv5',
    use_doc_orientation_classify=True,
    use_textline_orientation=True,
    text_det_thresh=0.3,
    text_rec_score_thresh=0.5
)
```

---

## PPStructureV3 - 文档解析

解析复杂文档，支持表格、公式、印章、图表识别。

### 导入

```python
from paddleocr import PPStructureV3
```

### 功能开关

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_doc_orientation_classify` | bool | `False` | 文档方向分类 |
| `use_doc_unwarping` | bool | `False` | 弯曲矫正 |
| `use_textline_orientation` | bool | `False` | 文本行方向分类 |
| `use_seal_recognition` | bool | `False` | 印章识别 |
| `use_table_recognition` | bool | `True` | 表格识别 |
| `use_formula_recognition` | bool | `False` | 公式识别 |
| `use_chart_recognition` | bool | `False` | 图表识别 |
| `use_region_detection` | bool | `False` | 区域检测 |

### 版面检测参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `layout_threshold` | float | 版面检测阈值 |
| `layout_nms` | bool | 是否使用 NMS |
| `layout_unclip_ratio` | float | 版面扩展系数 |
| `layout_merge_bboxes_mode` | str | 重叠框过滤方法 |

### 印章识别参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `seal_det_limit_side_len` | int | 印章检测边长限制 |
| `seal_det_thresh` | float | 印章检测阈值 |
| `seal_det_box_thresh` | float | 印章框阈值 |
| `seal_det_unclip_ratio` | float | 印章区域扩展 |
| `seal_rec_score_thresh` | float | 印章识别阈值 |

### 表格识别参数 (predict 方法)

| 参数 | 类型 | 说明 |
|------|------|------|
| `use_wired_table_cells_trans_to_html` | bool | 有线表格转 HTML |
| `use_wireless_table_cells_trans_to_html` | bool | 无线表格转 HTML |
| `use_table_orientation_classify` | bool | 表格方向分类 |
| `use_e2e_wired_table_rec_model` | bool | 端到端有线表格模型 |
| `use_e2e_wireless_table_rec_model` | bool | 端到端无线表格模型 |

### 使用示例

```python
from paddleocr import PPStructureV3

# 完整文档解析
pipeline = PPStructureV3(
    use_table_recognition=True,
    use_formula_recognition=True,
    use_seal_recognition=True,
    use_chart_recognition=True
)

result = pipeline.predict(input='document.pdf')

for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')
    res.save_to_json(save_path='output/')

# 仅表格识别
pipeline = PPStructureV3(
    use_table_recognition=True,
    use_formula_recognition=False,
    use_seal_recognition=False
)
```

### 方法

| 方法 | 说明 |
|------|------|
| `predict(input)` | 执行预测 |
| `predict_iter(input)` | 迭代式预测 |
| `concatenate_markdown_pages(markdown_list)` | 合并多页 Markdown |

---

## PPChatOCRv4Doc - 智能抽取

从票据、证件、合同中智能提取信息。

### 导入

```python
from paddleocr import PPChatOCRv4Doc
```

### 特有参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `retriever_config` | dict | 检索器配置 (embedding 模型) |
| `mllm_chat_bot_config` | dict | 多模态 LLM 配置 |
| `chat_bot_config` | dict | LLM 配置 |

### 配置示例

```python
# ERNIE API 配置
chat_bot_config = {
    "module_name": "chat_bot",
    "model_name": "ernie-3.5-8k",
    "base_url": "https://qianfan.baidubce.com/v2",
    "api_type": "openai",
    "api_key": "your_api_key"
}

# PP-DocBee 本地配置
mllm_chat_bot_config = {
    "module_name": "chat_bot",
    "model_name": "PP-DocBee",
    "base_url": "http://localhost:8000",
    "api_type": "openai",
    "api_key": "fake_key"
}
```

### 使用示例

```python
from paddleocr import PPChatOCRv4Doc

# 离线模式（使用 PP-DocBee2）
chat_ocr = PPChatOCRv4Doc(
    use_seal_recognition=True,
    use_table_recognition=True
)

# 视觉分析
visual_result = chat_ocr.visual_predict(input='invoice.png')

# 构建向量
vector_info = chat_ocr.build_vector(visual_result)

# 信息抽取
result = chat_ocr.chat(
    key_list=['发票号码', '金额', '日期'],
    visual_info=visual_result,
    vector_info=vector_info
)

print(result['chat_res'])
```

### 方法

| 方法 | 说明 |
|------|------|
| `visual_predict(input)` | 视觉分析 |
| `build_vector(visual_info)` | 构建向量索引 |
| `chat(key_list, visual_info, ...)` | 信息抽取 |
| `mllm_pred(input, key_list)` | 多模态 LLM 预测 |
| `save_vector(vector_info, save_path)` | 保存向量 |
| `load_vector(data_path)` | 加载向量 |

---

## PaddleOCRVL - 视觉语言模型

使用 VLM 进行复杂文档理解。

### 平台限制

> ⚠️ **不支持 macOS ARM (M1/M2/M3/M4)**

### 导入

```python
from paddleocr import PaddleOCRVL
```

### 特有参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `vl_rec_backend` | str | 后端 (`native`/`vllm-server`/`sglang-server`/`fastdeploy-server`) |
| `vl_rec_server_url` | str | 服务器 URL |
| `vl_rec_max_concurrency` | int | 最大并发数 |
| `vl_rec_api_key` | str | API Key |
| `use_layout_detection` | bool | 版面检测 |
| `use_chart_recognition` | bool | 图表识别 |
| `format_block_content` | bool | 格式化块内容 |

### 生成参数 (predict 方法)

| 参数 | 类型 | 说明 |
|------|------|------|
| `temperature` | float | 生成温度 |
| `top_p` | float | 核采样概率 |
| `repetition_penalty` | float | 重复惩罚 |
| `min_pixels` | int | 最小像素 |
| `max_pixels` | int | 最大像素 |
| `prompt_label` | str | 提示标签 |

### 使用示例

```python
from paddleocr import PaddleOCRVL

# 本地推理
vl = PaddleOCRVL(
    use_doc_orientation_classify=True,
    use_layout_detection=True
)

result = vl.predict('complex_document.pdf')

for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')

# 使用服务器后端
vl = PaddleOCRVL(
    vl_rec_backend='vllm-server',
    vl_rec_server_url='http://localhost:8000'
)
```

---

## DocPreprocessor - 文档预处理

专门用于文档预处理（方向矫正、弯曲矫正）。

### 导入

```python
from paddleocr import DocPreprocessor
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `use_doc_orientation_classify` | bool | 文档方向分类 (0°/90°/180°/270°) |
| `use_doc_unwarping` | bool | 弯曲文档矫正 |

### 使用示例

```python
from paddleocr import DocPreprocessor

# 完整预处理
preprocessor = DocPreprocessor(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True
)

result = preprocessor.predict(input='curved_doc.png')

for res in result:
    res.save_to_img(save_path='output/')
```

---

## PPDocTranslation - 文档翻译

保持版面结构的文档翻译。

### 导入

```python
from paddleocr import PPDocTranslation
```

### 特有参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `chat_bot_config` | dict | LLM 翻译配置 |

### 使用示例

```python
from paddleocr import PPDocTranslation

chat_bot_config = {
    "module_name": "chat_bot",
    "model_name": "ernie-3.5-8k",
    "base_url": "https://qianfan.baidubce.com/v2",
    "api_type": "openai",
    "api_key": "your_api_key"
}

translator = PPDocTranslation(
    use_table_recognition=True,
    chat_bot_config=chat_bot_config
)

# 视觉分析
visual_result = translator.visual_predict(input='english_doc.pdf')

# 翻译（需要 LLM API）
# translated = translator.translate(visual_result, source_lang='en', target_lang='zh')
```

---

## SealRecognition - 印章识别

独立的印章识别 Pipeline。

### 导入

```python
from paddleocr import SealRecognition
```

### 使用示例

```python
from paddleocr import SealRecognition

seal_ocr = SealRecognition(
    use_layout_detection=True,
    seal_det_thresh=0.3
)

result = seal_ocr.predict(input='document_with_seal.png')

for res in result:
    res.print()
```

---

## 通用参数说明

### 模型配置参数

所有 Pipeline 支持自定义模型路径：

| 参数模式 | 说明 |
|----------|------|
| `*_model_name` | 模型名称（自动下载） |
| `*_model_dir` | 本地模型路径 |
| `*_batch_size` | 批次大小 |

### 结果对象方法

所有 `predict()` 返回的结果对象支持：

| 方法 | 说明 |
|------|------|
| `res.print()` | 打印结果 |
| `res.json` | 获取 JSON 格式 |
| `res.markdown` | 获取 Markdown 格式 |
| `res.save_to_json(save_path)` | 保存为 JSON |
| `res.save_to_markdown(save_path)` | 保存为 Markdown |
| `res.save_to_img(save_path)` | 保存可视化图片 |

---

## 支持的语言列表

### PP-OCRv5 支持

| 语言组 | 语言代码 |
|--------|----------|
| 中文 | `ch`, `chinese_cht` |
| 英文 | `en` |
| 日韩 | `japan`, `korean` |
| 拉丁系 | `fr`, `de`, `es`, `it`, `pt`, `nl`, `pl`, `vi` 等 |
| 斯拉夫系 | `ru`, `be`, `uk` |
| 阿拉伯系 | `ar`, `fa`, `ug`, `ur` |
| 天城文系 | `hi`, `mr`, `ne` 等 |
| 其他 | `th`, `el`, `te`, `ta` |

### 完整语言列表

```python
# 拉丁系 (50+)
LATIN_LANGS = [
    "af", "az", "bs", "cs", "cy", "da", "de", "es", "et", "fr",
    "ga", "hr", "hu", "id", "is", "it", "ku", "la", "lt", "lv",
    "mi", "ms", "mt", "nl", "no", "oc", "pi", "pl", "pt", "ro",
    "sk", "sl", "sq", "sv", "sw", "tl", "tr", "uz", "vi", "french",
    "german", "fi", "eu", "gl", "lb", "rm", "ca", "qu"
]

# 阿拉伯系
ARABIC_LANGS = ["ar", "fa", "ug", "ur", "ps", "ku", "sd", "bal"]

# 斯拉夫系
CYRILLIC_LANGS = [
    "ru", "rs_cyrillic", "be", "bg", "uk", "mn", "kk", "ky", "tg", "mk"
]

# 天城文系
DEVANAGARI_LANGS = [
    "hi", "mr", "ne", "bh", "mai", "ang", "bho", "mah", "sck", "new",
    "gom", "sa", "bgc"
]
```

---

## 版本历史

| 版本 | 主要变化 |
|------|----------|
| PP-OCRv5 | 默认版本，较 v4 提升 13% |
| PP-OCRv4 | 移动端优化 |
| PP-OCRv3 | 更多语言支持 |

---

## 相关链接

- [PaddleOCR 官方文档](https://paddleocr.ai/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [示例代码](../../examples/)
