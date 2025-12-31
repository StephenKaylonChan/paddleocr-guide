---
description: 每周维护，归档历史记录，更新项目状态
allowed-tools: Read, Edit, Write, Bash(date)
---

# /weekly 命令

每周执行一次，进行项目维护和历史归档。

## 执行流程

### Step 1: 归档 CURRENT.md

1. 读取 `docs/ai-context/CURRENT.md`
2. 将「最近完成」中超过一周的条目移动到归档文件
3. 创建归档文件: `docs/ai-context/archive/YYYY-MM-DD.md`

### Step 2: 更新 CONTEXT.md

检查 `docs/ai-context/CONTEXT.md` 是否需要更新：
- 项目阶段变化
- 开发状态变化
- 新增重要约束

### Step 3: 清理 CURRENT.md

- 保留最近一周的记录
- 更新「归档记录」表格
- 重置「本周焦点」

### Step 4: 输出报告

```
✅ 每周维护完成

## 归档
- 归档条目: [N] 条
- 归档文件: docs/ai-context/archive/YYYY-MM-DD.md

## 更新
- CONTEXT.md: [是/否]
- CURRENT.md: 已清理

## Token 状态
- CONTEXT.md: ~[N] tokens
- CURRENT.md: ~[N] tokens

📅 [当前日期]
```

## 使用示例

```
/weekly
```

## 归档策略

### 归档文件格式

```markdown
# 归档记录 YYYY-MM-DD

**归档周期**: YYYY-MM-DD ~ YYYY-MM-DD

## 完成任务

| 日期 | 任务 | 状态 |
|------|------|------|
| ... | ... | ✅ |
```

## 注意事项

- 每周结束时或 CURRENT.md 过长时使用
- 确保归档后 CURRENT.md < 1000 tokens
- 月度归档已合并到此命令
