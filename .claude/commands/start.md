---
description: 恢复项目记忆，快速进入开发状态
argument-hint: [--full | --example]
allowed-tools: Read, Bash(date)
---

# /start 命令

恢复项目上下文，快速进入开发状态。

## 执行流程

### Step 1: 读取核心文档

**必读**（默认模式）：
1. `docs/ai-context/CONTEXT.md` - 项目快照
2. `docs/ai-context/CURRENT.md` - 当前进度

**--full 模式额外读取**：
- `docs/development/examples.md`
- `docs/development/DEVELOPMENT.md`
- `README.md`

**--example 模式额外读取**：
- `docs/development/examples.md`
- `examples/README.md`

### Step 2: 输出确认

读取完成后，输出以下格式确认：

```
✅ 已恢复上下文

**项目**: paddleocr-guide
**阶段**: [从 CONTEXT.md 获取]
**状态**: [从 CURRENT.md 获取]

**下一步**: [从 CURRENT.md 的"下一步"获取]
```

## 使用示例

```
/start           # 快速启动（默认）
/start --full    # 完整启动，读取所有文档
/start --example # 示例开发模式
```

## Token 预算

- 默认模式: < 2500 tokens
- --full 模式: < 4000 tokens
