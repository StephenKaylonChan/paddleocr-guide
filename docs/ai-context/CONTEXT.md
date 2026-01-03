# 项目上下文（AI 快速恢复）

**最后更新**: 2026-01-03
**项目阶段**: Beta (0.3.0)
**当前状态**: 文档体系完善

---

## TL;DR（30秒速览）

| 属性 | 值 |
|------|-----|
| **项目名称** | paddleocr-guide |
| **项目性质** | PaddleOCR 3.0 中文实战指南 |
| **技术栈** | Python 3.8+ / PaddleOCR 3.x / PaddlePaddle |
| **核心特点** | 中文社区 / macOS 优化 / CLI 工具 |
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
- 中文 README（面向中文社区）
- **16 个示例代码** (basic/3, document/3, advanced/10)
- **公共模块** (examples/_common/)
- **完整文档体系** (docs/zh/, 17 个文档)
  - 核心文档（installation, api_reference, model_comparison, troubleshooting）
  - **新增 7 个文档** (v0.3.0):
    - quickstart.md (快速入门)
    - performance.md (性能优化)
    - case_studies.md (实际案例)
    - best_practices.md (最佳实践)
    - error_codes.md (错误代码)
    - deployment.md (部署指南)
    - README.md (文档导航)
- **测试框架** (tests/, 27个用例)
- **CI/CD** (GitHub Actions)
- **CLI 命令行工具** (paddleocr-guide, 5个命令)
- **pre-commit hooks**
- GitHub 仓库

### 📋 待开发
- 更多集成测试
- Web UI（可选）
- 视频教程（可选）

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
│   │   └── guides/         # AI 配置指南
│   ├── development/        # 开发文档
│   └── zh/                 # 中文文档
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
