# PaddleOCR 3.x API Reference

> Complete API documentation based on source code analysis

---

## Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [PaddleOCR - General OCR](#paddleocr---general-ocr)
- [PPStructureV3 - Document Parsing](#ppstructurev3---document-parsing)
- [PPChatOCRv4Doc - Intelligent Extraction](#ppchatocrv4doc---intelligent-extraction)
- [PaddleOCRVL - Vision Language Model](#paddleocrvl---vision-language-model)
- [DocPreprocessor - Document Preprocessing](#docpreprocessor---document-preprocessing)
- [PPDocTranslation - Document Translation](#ppdoctranslation---document-translation)
- [SealRecognition - Seal Recognition](#sealrecognition---seal-recognition)
- [Common Parameters](#common-parameters)
- [Supported Languages](#supported-languages)

---

## Pipeline Overview

PaddleOCR 3.x provides 10 high-level Pipelines:

| Pipeline | Function | macOS ARM | Use Case |
|----------|----------|-----------|----------|
| `PaddleOCR` | General OCR | ✅ | Image text recognition |
| `PPStructureV3` | Document parsing | ✅ | PDF/table/layout analysis |
| `PPChatOCRv4Doc` | Intelligent extraction | ✅ | Invoice/ID card info extraction |
| `PaddleOCRVL` | Vision language | ❌ | Complex document understanding |
| `DocPreprocessor` | Preprocessing | ✅ | Orientation/warping correction |
| `PPDocTranslation` | Translation | ✅* | Multi-language document translation |
| `SealRecognition` | Seal recognition | ✅ | Stamp/seal extraction |
| `FormulaRecognitionPipeline` | Formula recognition | ✅ | Math formula to LaTeX |
| `TableRecognitionPipelineV2` | Table recognition | ✅ | Table structure recognition |
| `DocUnderstanding` | Document understanding | ❌ | Document Q&A |

> *PPDocTranslation requires LLM API configuration

---

## PaddleOCR - General OCR

Basic OCR for recognizing text in images.

### Import

```python
from paddleocr import PaddleOCR
```

### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | str | `"ch"` | Language, see [Supported Languages](#supported-languages) |
| `ocr_version` | str | `"PP-OCRv5"` | OCR version (PP-OCRv3/v4/v5) |
| `use_doc_orientation_classify` | bool | `False` | Enable document orientation classification |
| `use_doc_unwarping` | bool | `False` | Enable warping correction |
| `use_textline_orientation` | bool | `False` | Enable text line orientation classification |

### Detection Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text_det_limit_side_len` | int | Detection image side length limit |
| `text_det_limit_type` | str | Side length limit type (`min`/`max`) |
| `text_det_thresh` | float | Detection pixel threshold (default 0.3) |
| `text_det_box_thresh` | float | Detection box threshold (default 0.6) |
| `text_det_unclip_ratio` | float | Text region expansion coefficient (default 1.5) |
| `text_det_input_shape` | tuple | Detection model input shape (C, H, W) |

### Recognition Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text_rec_score_thresh` | float | Recognition score threshold |
| `text_recognition_batch_size` | int | Recognition batch size |
| `return_word_box` | bool | Return word-level coordinates |
| `text_rec_input_shape` | tuple | Recognition model input shape |

### Usage Example

```python
from paddleocr import PaddleOCR

# Basic usage
ocr = PaddleOCR(lang='ch')
result = ocr.predict('image.png')

for res in result:
    res.print()

# Advanced configuration
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

## PPStructureV3 - Document Parsing

Parse complex documents, supporting tables, formulas, seals, and charts.

### Import

```python
from paddleocr import PPStructureV3
```

### Feature Switches

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_doc_orientation_classify` | bool | `False` | Document orientation classification |
| `use_doc_unwarping` | bool | `False` | Warping correction |
| `use_textline_orientation` | bool | `False` | Text line orientation classification |
| `use_seal_recognition` | bool | `False` | Seal recognition |
| `use_table_recognition` | bool | `True` | Table recognition |
| `use_formula_recognition` | bool | `False` | Formula recognition |
| `use_chart_recognition` | bool | `False` | Chart recognition |
| `use_region_detection` | bool | `False` | Region detection |

### Layout Detection Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `layout_threshold` | float | Layout detection threshold |
| `layout_nms` | bool | Use NMS |
| `layout_unclip_ratio` | float | Layout expansion coefficient |
| `layout_merge_bboxes_mode` | str | Overlapping box filtering method |

### Seal Recognition Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `seal_det_limit_side_len` | int | Seal detection side length limit |
| `seal_det_thresh` | float | Seal detection threshold |
| `seal_det_box_thresh` | float | Seal box threshold |
| `seal_det_unclip_ratio` | float | Seal region expansion |
| `seal_rec_score_thresh` | float | Seal recognition threshold |

### Table Recognition Parameters (predict method)

| Parameter | Type | Description |
|-----------|------|-------------|
| `use_wired_table_cells_trans_to_html` | bool | Wired table to HTML |
| `use_wireless_table_cells_trans_to_html` | bool | Wireless table to HTML |
| `use_table_orientation_classify` | bool | Table orientation classification |
| `use_e2e_wired_table_rec_model` | bool | End-to-end wired table model |
| `use_e2e_wireless_table_rec_model` | bool | End-to-end wireless table model |

### Usage Example

```python
from paddleocr import PPStructureV3

# Complete document parsing
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

# Table recognition only
pipeline = PPStructureV3(
    use_table_recognition=True,
    use_formula_recognition=False,
    use_seal_recognition=False
)
```

### Methods

| Method | Description |
|--------|-------------|
| `predict(input)` | Execute prediction |
| `predict_iter(input)` | Iterative prediction |
| `concatenate_markdown_pages(markdown_list)` | Merge multi-page Markdown |

---

## PPChatOCRv4Doc - Intelligent Extraction

Intelligently extract information from invoices, IDs, and contracts.

### Import

```python
from paddleocr import PPChatOCRv4Doc
```

### Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `retriever_config` | dict | Retriever configuration (embedding model) |
| `mllm_chat_bot_config` | dict | Multimodal LLM configuration |
| `chat_bot_config` | dict | LLM configuration |

### Configuration Example

```python
# ERNIE API configuration
chat_bot_config = {
    "module_name": "chat_bot",
    "model_name": "ernie-3.5-8k",
    "base_url": "https://qianfan.baidubce.com/v2",
    "api_type": "openai",
    "api_key": "your_api_key"
}

# PP-DocBee local configuration
mllm_chat_bot_config = {
    "module_name": "chat_bot",
    "model_name": "PP-DocBee",
    "base_url": "http://localhost:8000",
    "api_type": "openai",
    "api_key": "fake_key"
}
```

### Usage Example

```python
from paddleocr import PPChatOCRv4Doc

# Offline mode (using PP-DocBee2)
chat_ocr = PPChatOCRv4Doc(
    use_seal_recognition=True,
    use_table_recognition=True
)

# Visual analysis
visual_result = chat_ocr.visual_predict(input='invoice.png')

# Build vector
vector_info = chat_ocr.build_vector(visual_result)

# Information extraction
result = chat_ocr.chat(
    key_list=['Invoice Number', 'Amount', 'Date'],
    visual_info=visual_result,
    vector_info=vector_info
)

print(result['chat_res'])
```

### Methods

| Method | Description |
|--------|-------------|
| `visual_predict(input)` | Visual analysis |
| `build_vector(visual_info)` | Build vector index |
| `chat(key_list, visual_info, ...)` | Information extraction |
| `mllm_pred(input, key_list)` | Multimodal LLM prediction |
| `save_vector(vector_info, save_path)` | Save vector |
| `load_vector(data_path)` | Load vector |

---

## PaddleOCRVL - Vision Language Model

Use VLM for complex document understanding.

### Platform Limitation

> ⚠️ **NOT supported on macOS ARM (M1/M2/M3/M4)**

### Import

```python
from paddleocr import PaddleOCRVL
```

### Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `vl_rec_backend` | str | Backend (`native`/`vllm-server`/`sglang-server`/`fastdeploy-server`) |
| `vl_rec_server_url` | str | Server URL |
| `vl_rec_max_concurrency` | int | Maximum concurrency |
| `vl_rec_api_key` | str | API Key |
| `use_layout_detection` | bool | Layout detection |
| `use_chart_recognition` | bool | Chart recognition |
| `format_block_content` | bool | Format block content |

### Generation Parameters (predict method)

| Parameter | Type | Description |
|-----------|------|-------------|
| `temperature` | float | Generation temperature |
| `top_p` | float | Nucleus sampling probability |
| `repetition_penalty` | float | Repetition penalty |
| `min_pixels` | int | Minimum pixels |
| `max_pixels` | int | Maximum pixels |
| `prompt_label` | str | Prompt label |

### Usage Example

```python
from paddleocr import PaddleOCRVL

# Local inference
vl = PaddleOCRVL(
    use_doc_orientation_classify=True,
    use_layout_detection=True
)

result = vl.predict('complex_document.pdf')

for res in result:
    res.print()
    res.save_to_markdown(save_path='output/')

# Using server backend
vl = PaddleOCRVL(
    vl_rec_backend='vllm-server',
    vl_rec_server_url='http://localhost:8000'
)
```

---

## DocPreprocessor - Document Preprocessing

Specialized for document preprocessing (orientation correction, warping correction).

### Import

```python
from paddleocr import DocPreprocessor
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `use_doc_orientation_classify` | bool | Document orientation classification (0°/90°/180°/270°) |
| `use_doc_unwarping` | bool | Warped document correction |

### Usage Example

```python
from paddleocr import DocPreprocessor

# Complete preprocessing
preprocessor = DocPreprocessor(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True
)

result = preprocessor.predict(input='curved_doc.png')

for res in result:
    res.save_to_img(save_path='output/')
```

---

## PPDocTranslation - Document Translation

Document translation with preserved layout structure.

### Import

```python
from paddleocr import PPDocTranslation
```

### Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `chat_bot_config` | dict | LLM translation configuration |

### Usage Example

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

# Visual analysis
visual_result = translator.visual_predict(input='english_doc.pdf')

# Translation (requires LLM API)
# translated = translator.translate(visual_result, source_lang='en', target_lang='zh')
```

---

## SealRecognition - Seal Recognition

Standalone seal recognition Pipeline.

### Import

```python
from paddleocr import SealRecognition
```

### Usage Example

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

## Common Parameters

### Model Configuration Parameters

All Pipelines support custom model paths:

| Pattern | Description |
|---------|-------------|
| `*_model_name` | Model name (auto-download) |
| `*_model_dir` | Local model path |
| `*_batch_size` | Batch size |

### Result Object Methods

All result objects returned by `predict()` support:

| Method | Description |
|--------|-------------|
| `res.print()` | Print result |
| `res.json` | Get JSON format |
| `res.markdown` | Get Markdown format |
| `res.save_to_json(save_path)` | Save as JSON |
| `res.save_to_markdown(save_path)` | Save as Markdown |
| `res.save_to_img(save_path)` | Save visualization image |

---

## Supported Languages

### PP-OCRv5 Support

| Language Group | Language Codes |
|----------------|----------------|
| Chinese | `ch`, `chinese_cht` |
| English | `en` |
| Japanese/Korean | `japan`, `korean` |
| Latin | `fr`, `de`, `es`, `it`, `pt`, `nl`, `pl`, `vi`, etc. |
| Slavic | `ru`, `be`, `uk` |
| Arabic | `ar`, `fa`, `ug`, `ur` |
| Devanagari | `hi`, `mr`, `ne`, etc. |
| Others | `th`, `el`, `te`, `ta` |

### Complete Language List

```python
# Latin (50+)
LATIN_LANGS = [
    "af", "az", "bs", "cs", "cy", "da", "de", "es", "et", "fr",
    "ga", "hr", "hu", "id", "is", "it", "ku", "la", "lt", "lv",
    "mi", "ms", "mt", "nl", "no", "oc", "pi", "pl", "pt", "ro",
    "sk", "sl", "sq", "sv", "sw", "tl", "tr", "uz", "vi", "french",
    "german", "fi", "eu", "gl", "lb", "rm", "ca", "qu"
]

# Arabic
ARABIC_LANGS = ["ar", "fa", "ug", "ur", "ps", "ku", "sd", "bal"]

# Cyrillic
CYRILLIC_LANGS = [
    "ru", "rs_cyrillic", "be", "bg", "uk", "mn", "kk", "ky", "tg", "mk"
]

# Devanagari
DEVANAGARI_LANGS = [
    "hi", "mr", "ne", "bh", "mai", "ang", "bho", "mah", "sck", "new",
    "gom", "sa", "bgc"
]
```

---

## Version History

| Version | Major Changes |
|---------|---------------|
| PP-OCRv5 | Default version, 13% improvement over v4 |
| PP-OCRv4 | Mobile optimization |
| PP-OCRv3 | More language support |

---

## Related Links

- [PaddleOCR Official Documentation](https://paddleocr.ai/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [Example Code](../../examples/)
