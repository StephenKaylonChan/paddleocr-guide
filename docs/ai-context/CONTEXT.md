# 项目上下文（AI 快速恢复）

**最后更新**: 2025-12-31
**项目阶段**: Beta (0.1.0)
**当前状态**: 初始开发

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
- 6 个示例代码（examples/basic/, examples/document/）
- 中文文档（docs/zh/）
- GitHub 仓库

### 📋 待开发
- 高级示例（advanced/）
- 单元测试
- CI/CD 配置

---

## 目录结构速查

```
paddleocr-guide/
├── examples/           # 示例代码
│   ├── basic/          # 基础 OCR（3 个）
│   └── document/       # 文档处理（3 个）
├── docs/
│   ├── ai-context/     # AI 记忆层
│   ├── development/    # 开发文档
│   └── zh/             # 用户文档
└── assets/             # 资源文件
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
