---
description: 阶段性保存进度，更新 CURRENT.md
argument-hint: [checkpoint description]
allowed-tools: Read, Edit, Write, Bash(date)
---

# /checkpoint 命令

在完成重要阶段后保存进度。

## 执行流程

### Step 1: 确认保存内容

询问用户本次检查点的主要内容（如果未提供参数）。

### Step 2: 更新 CURRENT.md

更新 `docs/ai-context/CURRENT.md`：

1. 在「最近完成」表格添加新条目
2. 更新「当前任务」状态
3. 必要时调整「下一步」

### Step 3: 输出确认

```
✅ 检查点已保存

**保存内容**: [用户提供的描述]
**更新文件**: docs/ai-context/CURRENT.md
**时间**: [当前日期]
```

## 使用示例

```
/checkpoint 完成基础示例编写
/checkpoint 修复 macOS 兼容性问题
```

## 注意事项

- 每完成一个重要任务后使用
- 保持 CURRENT.md 内容简洁（< 1000 tokens）
- 内容过长时提醒使用 /weekly 归档
