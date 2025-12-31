# 项目上下文（AI 快速恢复）

**最后更新**: 2025-12-31
**项目阶段**: Beta (0.2.0)
**当前状态**: 功能完整

---

## TL;DR（30秒速览）

| 属性 | 值 |
|------|-----|
| **项目名称** | paddleocr-guide |
| **项目性质** | PaddleOCR 3.0 中文实战指南 |
| **技术栈** | Python 3.8+ / PaddleOCR 3.0 / PaddlePaddle |
| **核心特点** | 中英双语 / macOS 优化 / 教学示例 |
| **仓库地址** | [stephenkaylonchan/paddleocr-guide](https://github.com/stephenkaylonchan/paddleocr-guide) |

---

## 关键技术约束

### macOS ARM 兼容性（重要）

| 模型 | macOS ARM | 说明 |
|------|-----------|------|
| PP-OCRv5 | ✅ | 推荐，~10MB |
| PP-StructureV3 | ✅ | 文档/表格 |
| PP-ChatOCRv4 | ✅ | 需 ERNIE API |
| **PaddleOCR-VL** | ❌ | **不支持 M1/M2/M3/M4** |

---

## 当前开发状态

### ✅ 已完成
- 项目初始化（pyproject.toml, .gitignore, LICENSE）
- 中英文 README
- **16 个示例代码**：
  - basic/ (3个): 基础 OCR、批量处理、多语言
  - document/ (3个): PDF 转换、表格识别、版面分析
  - advanced/ (10个): 印章、公式、图表、智能抽取、手写、竖排、预处理、VL、翻译、理解
- 中文文档（docs/zh/）
- GitHub 仓库
- **PaddleOCR 3.x API 全面适配**
- **10 个 Pipeline 100% 覆盖**
- **完整 API 参考文档** (docs/zh/api_reference.md)

### 📋 待开发
- 单元测试
- CI/CD 配置
- 英文文档同步

---

## 目录结构速查

```
paddleocr-guide/
├── examples/               # 示例代码 (16个)
│   ├── basic/              # 基础 OCR（3 个）- PP-OCRv5
│   ├── document/           # 文档处理（3 个）- PP-StructureV3
│   └── advanced/           # 高级示例（10 个）
│       ├── 01-03           # PP-StructureV3 子功能
│       ├── 04              # PP-ChatOCRv4Doc
│       ├── 05-07           # PP-OCRv5 高级用法
│       ├── 08              # PaddleOCR-VL (非ARM)
│       ├── 09              # PP-DocTranslation
│       └── 10              # DocUnderstanding
├── docs/
│   ├── ai-context/         # AI 记忆层
│   ├── development/        # 开发文档
│   └── zh/                 # 用户文档 + API 参考
└── assets/                 # 资源文件
```

---

## 协作偏好

- ✅ 每次只执行一步
- ✅ 中文为主
- ✅ 保持示例代码简洁
- ✅ 遵循 PEP 8 / black / isort

---

## 快速导航

- [当前进度](CURRENT.md)
- [示例说明](../development/examples.md)
- [开发规范](../development/DEVELOPMENT.md)
