# 项目上下文（AI 快速恢复）

**最后更新**: 2025-12-31
**项目阶段**: Beta (0.2.1)
**当前状态**: 功能完整

---

## TL;DR（30秒速览）

| 属性 | 值 |
|------|-----|
| **项目名称** | paddleocr-guide |
| **项目性质** | PaddleOCR 3.0 中文实战指南 |
| **技术栈** | Python 3.8+ / PaddleOCR 3.x / PaddlePaddle |
| **核心特点** | 中英双语 / macOS 优化 / CLI 工具 |
| **仓库地址** | [StephenKaylonChan/paddleocr-guide](https://github.com/StephenKaylonChan/paddleocr-guide) |

---

## 关键技术约束

### macOS ARM 兼容性（重要）

| 模型 | macOS ARM | 说明 |
|------|-----------|------|
| PP-OCRv5 | ✅ | 推荐，~10MB |
| PP-StructureV3 | ✅ | 文档/表格 |
| PP-ChatOCRv4 | ✅ | 需 ERNIE API |
| **PaddleOCR-VL** | ❌ | **不支持 M1/M2/M3/M4** |

### ⚠️ 已知严重问题

**PaddleOCR 3.x 内存占用过高**:
- macOS ARM 上可能占用 **40GB+ 内存**
- 可能导致系统卡死
- 详见 [CURRENT.md](CURRENT.md) 待排查问题

---

## 当前开发状态

### ✅ 已完成
- 项目初始化（pyproject.toml, .gitignore, LICENSE）
- 中英文 README
- **16 个示例代码** (basic/3, document/3, advanced/10)
- **公共模块** (examples/_common/)
- 中英文文档（docs/zh/, docs/en/）
- **测试框架** (tests/, 27个用例)
- **CI/CD** (GitHub Actions)
- **CLI 命令行工具** (paddleocr-guide)
- **pre-commit hooks**
- GitHub 仓库

### 📋 待开发
- 排查内存问题（优先）
- 更多集成测试
- Docker 支持

---

## 目录结构速查

```
paddleocr-guide/
├── paddleocr_guide/        # CLI 工具
│   └── cli.py              # 命令行入口
├── examples/               # 示例代码 (16个)
│   ├── _common/            # 公共模块
│   ├── basic/              # 基础 OCR（3 个）
│   ├── document/           # 文档处理（3 个）
│   └── advanced/           # 高级示例（10 个）
├── tests/                  # 测试代码
├── docs/
│   ├── ai-context/         # AI 记忆层
│   ├── development/        # 开发文档
│   ├── zh/                 # 中文文档
│   └── en/                 # 英文文档
├── .github/workflows/      # CI/CD
└── assets/                 # 资源文件
```

---

## 协作偏好

- ✅ 每次只执行一步
- ✅ 中文为主
- ✅ 保持示例代码简洁
- ✅ 遵循 PEP 8 / black / isort
- ⚠️ **暂时避免运行 OCR 测试** (内存问题)

---

## 快速导航

- [当前进度](CURRENT.md)
- [示例说明](../development/examples.md)
- [开发规范](../development/DEVELOPMENT.md)
