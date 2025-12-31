# Slash Commands 完整配置

> 8 个核心命令的完整 .md 文件内容 - 可直接复制到 `.claude/commands/` 目录使用

**文档性质**: 通用配置参考（可跨项目复用）
**版本**: v2.3
**命令数量**: 8 个

---

## 目录

1. [命令总览](#1-命令总览)
2. [/start - 恢复项目记忆](#2-start---恢复项目记忆)
3. [/checkpoint - 阶段性保存](#3-checkpoint---阶段性保存)
4. [/end - 每日结束](#4-end---每日结束)
5. [/weekly - 每周优化](#5-weekly---每周优化)
6. [/monthly - 每月归档](#6-monthly---每月归档)
7. [/audit - 项目健康检查](#7-audit---项目健康检查)
8. [/deep-audit - 全面深度审计](#8-deep-audit---全面深度审计)
9. [/fix - ESLint 自动修复](#9-fix---eslint-自动修复)
10. [安装说明](#10-安装说明)

---

## 1. 命令总览

| 命令 | 文件 | 用途 | 常用参数 |
|------|------|------|----------|
| `/start` | start.md | 恢复项目记忆 | `--full`, `--bug`, `--api` |
| `/checkpoint` | checkpoint.md | 阶段性保存进度 | `--commit`, `--skip-git` |
| `/end` | end.md | 每日结束 | `--push`, `--no-push` |
| `/weekly` | weekly.md | 每周文档优化 | `--push` |
| `/monthly` | monthly.md | 每月归档 | `--push` |
| `/audit` | audit.md | 项目健康检查 | `--quick`, `--full`, `--security`, `--docs` |
| `/deep-audit` | deep-audit.md | 全面深度审计 | `--no-fix`, `--no-push` |
| `/fix` | fix.md | ESLint 自动修复 | `--check`, `--staged` |

---

## 2. /start - 恢复项目记忆

> 文件路径: `.claude/commands/start.md`

```markdown
---
description: 恢复项目记忆，快速进入开发状态
argument-hint: [--full | --bug | --api | --component | --deploy]
allowed-tools: Read, Bash(date)
---

<task>
恢复项目上下文，让 AI 快速理解项目状态，准备开始开发。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

运行以下命令获取时间信息：

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_WEEK_NUM=$(date +%V)
echo "当前时间: $CURRENT_DATE $CURRENT_TIME (第 $CURRENT_WEEK_NUM 周)"
```

## Step 1: 解析参数

根据用户输入的参数确定读取范围：

| 参数 | 读取文档 | 场景 |
|------|----------|------|
| 无参数 / `--quick` | CONTEXT.md + CURRENT.md | 日常快速启动 |
| `--full` | 全部核心文档 | 首次使用或长时间未开发 |
| `--bug` | + troubleshooting.md | Bug 修复场景 |
| `--api` | + api.md + database.md | API 开发场景 |
| `--component` | + components.md | 组件开发场景 |
| `--deploy` | + DEPLOYMENT.md | 部署场景 |

## Step 2: 读取核心文档（必读）

**必读文档**（所有模式）：
1. `docs/ai-context/CONTEXT.md` - 项目快照
2. `docs/ai-context/CURRENT.md` - 当前进度

## Step 3: 根据参数读取额外文档

### --full 模式（完整启动）
额外读取：
- `docs/project/vision.md` - 项目愿景
- `docs/project/design.md` - 功能设计
- `docs/architecture/OVERVIEW.md` - 架构总览
- `docs/architecture/adr/README.md` - ADR 索引

### --bug 模式（Bug 修复）
额外读取：
- `docs/development/frontend/troubleshooting.md`
- `docs/development/backend/troubleshooting.md`

### --api 模式（API 开发）
额外读取：
- `docs/development/backend/api.md`
- `docs/development/backend/database.md`

### --component 模式（组件开发）
额外读取：
- `docs/development/frontend/components.md`
- `docs/development/frontend/pages.md`

### --deploy 模式（部署）
额外读取：
- `docs/project/DEPLOYMENT.md`

## Step 4: 验证理解并输出

输出格式：

```
✅ 已恢复上下文

## 验证理解

1. **项目类型**: [从 CONTEXT.md 获取]
2. **当前阶段**: [从 CONTEXT.md 获取]
3. **技术栈**: [前端框架] + [后端框架] + [数据库]
4. **下一步任务**: [从 CURRENT.md 获取 P0 任务]
5. **设计原则**: [从 CONTEXT.md 协作偏好获取]

## 本次读取的文档
- [x] CONTEXT.md
- [x] CURRENT.md
- [根据参数列出其他文档]

---

**已恢复上下文。当前阶段：[Phase X.Y]，下一步：[任务]。**
**我们从哪里开始？**
```

</workflow>
```

---

## 3. /checkpoint - 阶段性保存

> 文件路径: `.claude/commands/checkpoint.md`

```markdown
---
description: 阶段性保存开发进度，更新文档
argument-hint: [--commit | --skip-git]
allowed-tools: Read, Write, Edit, Bash(date, git)
---

<task>
完成一个功能/阶段后，更新开发文档，可选创建 Git commit。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)

# 获取星期
case $(date +%u) in
    1) DAY_NAME="周一" ;; 2) DAY_NAME="周二" ;;
    3) DAY_NAME="周三" ;; 4) DAY_NAME="周四" ;;
    5) DAY_NAME="周五" ;; 6) DAY_NAME="周六" ;;
    7) DAY_NAME="周日" ;;
esac

echo "当前时间: $CURRENT_DATE $CURRENT_TIME ($DAY_NAME)"
```

## Step 1: 总结当前工作

整理本阶段完成的工作：

1. **完成的工作**：列出已完成的功能/任务
2. **遇到的问题**：记录遇到的问题和解决方案
3. **剩余工作**：还需要完成的内容
4. **技术亮点**：值得记录的技术方案（如果有）

## Step 2: 更新 CURRENT.md

### 2.1 读取 CURRENT.md
```bash
# 读取当前内容
cat docs/ai-context/CURRENT.md
```

### 2.2 判断是否需要新增 Day 条目

检查今天（$CURRENT_DATE）是否已有 Day X 条目：
- **如果没有**：添加新的 Day X 条目
- **如果已有**：在该条目中追加本阶段工作内容

### 2.3 更新内容

在 Day X 条目中添加：
```markdown
### Day X - ${CURRENT_DATE}（${DAY_NAME}）⭐ [标题]

**工作时长**: Xh
**核心任务**: [任务描述]

**完成工作**：
- ✅ [工作内容 1]
- ✅ [工作内容 2]

**技术亮点**：
- [亮点描述]

**遇到的问题**：
- **问题**: [问题描述]
- **解决方案**: [解决方案]
```

### 2.4 更新任务列表

在"本周任务"部分，将已完成的任务标记为 ✅

## Step 3: 场景性更新（根据工作内容自动判断）

### Bug 修复场景
如果本次工作是修复 Bug：
- 创建或更新 `docs/development/[frontend|backend]/troubleshooting.md`
- 添加问题描述、原因、解决方案

### 组件开发场景
如果新增了组件：
- 更新 `docs/development/frontend/components.md`
- 添加组件的 Props、用途、示例

### API 开发场景
如果新增了 API：
- 更新 `docs/development/backend/api.md`
- 添加端点、请求/响应格式

## Step 4: Git 操作

### 参数处理
- `--commit`：自动创建 commit（不 push）
- `--skip-git`：跳过 Git 操作
- 无参数：询问用户是否需要 commit

### 创建 commit（如果需要）

```bash
# 检查是否有变更
git status --short

# 添加变更
git add docs/

# 创建 commit
git commit -m "$(cat <<'EOF'
docs: checkpoint - [简短描述本次工作]

- [工作内容 1]
- [工作内容 2]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Step 5: 输出检查点报告

```
## ✅ Checkpoint 完成

**时间**: ${CURRENT_DATE} ${CURRENT_TIME}

### 本阶段完成
- [工作内容 1]
- [工作内容 2]

### 更新的文档
- [x] CURRENT.md
- [根据场景列出其他更新的文档]

### Git 状态
- [ ] Commit 已创建 / 已跳过
- [ ] 未推送到远程

### 下一步
[根据 CURRENT.md 中的任务列表建议下一步]

---
继续开发，还是需要休息一下？
```

</workflow>
```

---

## 4. /end - 每日结束

> 文件路径: `.claude/commands/end.md`

```markdown
---
description: 每日开发结束，完整更新文档并提交
argument-hint: [--push | --no-push | --archive]
allowed-tools: Read, Write, Edit, Bash(date, git)
---

<task>
每日开发结束时，完整总结工作，更新文档，创建 commit 并可选推送。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_DAY=$(date +%d)

# 判断明天是否是下月第一天（用于归档判断）
# macOS
NEXT_DAY=$(date -v+1d +%d)
# Linux: NEXT_DAY=$(date -d tomorrow +%d)

if [ "$NEXT_DAY" == "01" ]; then
    NEED_ARCHIVE=true
    echo "提示：明天是新月份第一天，建议执行归档"
else
    NEED_ARCHIVE=false
fi

echo "当前时间: $CURRENT_DATE $CURRENT_TIME"
```

## Step 1: 总结本次会话

完整总结今天的工作：

1. **所有完成的工作**：列出今天完成的所有功能/任务
2. **遇到的问题和解决方案**：记录所有问题
3. **未完成的工作**：记录未完成的内容
4. **下次会话建议**：建议下次从哪里开始

## Step 2: 更新文档（完整更新）

### 2.1 更新 CURRENT.md

如果今天已经执行过 `/checkpoint`，补充完善内容。
如果没有执行过，创建完整的 Day X 条目。

更新内容：
- Day X 日志（完整版）
- 本周任务状态（标记完成的任务）
- 技术亮点（如果有新的）
- 问题与解决方案（如果有新的）

### 2.2 场景性文档更新

根据今天的工作内容，更新相关文档：
- Bug 修复 → troubleshooting.md
- 新组件 → components.md
- 新 API → api.md
- 新页面 → pages.md

### 2.3 检查是否需要更新 CONTEXT.md

如果今天有重大变化（如完成了一个 Phase、技术栈变更等）：
- 更新 CONTEXT.md 的"当前开发状态"
- 更新"下一步任务"

## Step 3: Git 操作（智能 commit）

### 3.1 检查今天是否已有 checkpoint commit

```bash
LAST_COMMIT_DATE=$(git log -1 --format=%cd --date=short 2>/dev/null || echo "")
LAST_COMMIT_MSG=$(git log -1 --format=%s 2>/dev/null || echo "")

echo "最新 commit: $LAST_COMMIT_DATE - $LAST_COMMIT_MSG"
```

### 3.2 决定 commit 策略

- 如果今天已有 checkpoint commit → 使用 `git commit --amend`
- 如果没有 → 创建新的 commit

### 3.3 创建 commit

```bash
# 添加所有变更
git add .

# 创建 commit（或 amend）
git commit -m "$(cat <<'EOF'
docs: 每日总结 ${CURRENT_DATE}

## 今日完成
- [工作内容 1]
- [工作内容 2]

## 技术亮点
- [亮点]

## 下次继续
- [待续任务]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3.4 推送处理

根据参数：
- `--push`：自动推送 `git push`
- `--no-push`：不推送
- 无参数：询问用户是否需要推送

## Step 4: 归档判断（仅月末）

如果 `NEED_ARCHIVE=true` 或用户指定 `--archive`：

提示用户：
```
⚠️ 检测到明天是新月份，建议执行归档：
- 执行 /monthly 进行归档
- 或在明天开始时执行
```

## Step 5: 输出完成报告

```
## ✅ 每日总结完成

**日期**: ${CURRENT_DATE} ${CURRENT_TIME}

### 今日完成
- [工作内容 1]
- [工作内容 2]
- [工作内容 3]

### 遇到的问题
- [问题 1]: [解决方案]

### 更新的文档
- [x] CURRENT.md
- [其他更新的文档]

### Git 状态
- [x] Commit 已创建
- [ ] 已推送 / 未推送

### 下次会话建议
1. 执行 `/start` 恢复上下文
2. 继续 [任务名称]
3. [其他建议]

---
辛苦了！明天见 👋
```

</workflow>
```

---

## 5. /weekly - 每周优化

> 文件路径: `.claude/commands/weekly.md`

```markdown
---
description: 每周文档优化，删除冗余，统计周报
argument-hint: [--push | --no-push]
allowed-tools: Read, Write, Edit, Bash(date, git, wc)
---

<task>
每周（建议周日）执行，优化文档，删除冗余内容，生成周报。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_WEEK_NUM=$(date +%V)

# 获取本周起止日期（macOS）
WEEK_START=$(date -v-$(( $(date +%u) - 1 ))d +%Y-%m-%d)
WEEK_END=$(date -v+$(( 7 - $(date +%u) ))d +%Y-%m-%d)

# Linux 版本:
# WEEK_START=$(date -d "last monday" +%Y-%m-%d)
# WEEK_END=$(date -d "next sunday" +%Y-%m-%d)

echo "第 $CURRENT_WEEK_NUM 周: $WEEK_START - $WEEK_END"
```

## Step 1: 审查 CURRENT.md

### 1.1 读取并分析

```bash
# 统计行数（估算 Token，每行约 10 tokens）
wc -l docs/ai-context/CURRENT.md
```

### 1.2 识别冗余内容

检查以下冗余类型：
- **重复日志**：相同内容出现多次
- **过度详细**：包含完整代码片段、过长的描述
- **已完成任务**：仍在"本周任务"中但已标记 ✅ 的过期任务
- **过时信息**：不再相关的技术亮点或问题

### 1.3 优化 CURRENT.md

执行优化：
1. 删除重复内容
2. 压缩过度详细的日志（保留关键信息）
3. 清理已完成的任务
4. 更新"本周时间"为下周

## Step 2: 审查其他文档

### 2.1 troubleshooting 文档
- 检查是否有已修复且不再相关的问题
- 检查是否有重复的问题记录

### 2.2 components.md / api.md
- 检查是否与代码同步（是否有遗漏或过时）

### 2.3 CONTEXT.md
- 检查"当前状态"是否准确
- 检查"下一步任务"是否需要更新

## Step 3: Token 优化报告

```bash
# 统计优化前后的行数
echo "=== Token 优化报告 ==="
echo "CURRENT.md: $(wc -l < docs/ai-context/CURRENT.md) 行"
echo "CONTEXT.md: $(wc -l < docs/ai-context/CONTEXT.md) 行"
```

计算优化效果：
- 优化前 Token（估算）
- 优化后 Token
- 节省百分比

## Step 4: 更新 CONTEXT.md

如果本周有显著进展：
1. 更新"当前开发状态"
2. 更新"下一步任务"（P1 → P2 任务流转）
3. 更新"最后更新"时间

## Step 5: 统计本周工作

```bash
# 统计本周 commits
git log --since="$WEEK_START" --until="$WEEK_END 23:59:59" --oneline | wc -l
```

汇总：
- 本周工作时长
- 本周 commits 数
- 完成的功能/任务数
- 修复的 Bug 数

## Step 6: Git 操作

```bash
git add docs/
git commit -m "$(cat <<'EOF'
docs: 第 ${CURRENT_WEEK_NUM} 周优化

## 优化内容
- 清理 CURRENT.md 冗余内容
- 更新文档同步状态
- Token 优化: [X]% 减少

## 本周统计
- Commits: [X] 次
- 完成功能: [X] 个

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

根据参数决定是否推送。

## Step 7: 输出周报

```
## 📊 第 ${CURRENT_WEEK_NUM} 周周报

**周期**: ${WEEK_START} - ${WEEK_END}
**生成时间**: ${CURRENT_DATE} ${CURRENT_TIME}

---

### 本周完成
- [功能 1]
- [功能 2]
- [功能 3]

### 本周统计
| 指标 | 数值 |
|------|------|
| 工作时长 | Xh |
| Commits | X 次 |
| 新增功能 | X 个 |
| Bug 修复 | X 个 |

### Token 优化
| 文档 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| CURRENT.md | ~X tokens | ~X tokens | X% |

### 下周计划
1. [任务 1]
2. [任务 2]

---
周报已生成，继续加油！💪
```

</workflow>
```

---

## 6. /monthly - 每月归档

> 文件路径: `.claude/commands/monthly.md`

```markdown
---
description: 每月归档 CURRENT.md，创建新月份模板
argument-hint: [--push | --no-push]
allowed-tools: Read, Write, Edit, Bash(date, git, cp, wc)
---

<task>
每月初执行，归档上月 CURRENT.md，创建新月份模板，全面审查文档。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_MONTH=$(date +%Y-%m)
CURRENT_WEEK_NUM=$(date +%V)

# 获取上月信息（用于归档命名）
# macOS
LAST_MONTH=$(date -v-1m +%Y-%m)
# Linux: LAST_MONTH=$(date -d "last month" +%Y-%m)

echo "当前月份: $CURRENT_MONTH"
echo "归档月份: $LAST_MONTH"
```

## Step 1: 归档 CURRENT.md

### 1.1 复制到归档目录

```bash
# 创建归档目录（如果不存在）
mkdir -p docs/ai-context/archive

# 复制当前 CURRENT.md 到归档
cp docs/ai-context/CURRENT.md "docs/ai-context/archive/${LAST_MONTH}.md"

echo "已归档到: docs/ai-context/archive/${LAST_MONTH}.md"
```

### 1.2 创建新月份 CURRENT.md

创建新的 CURRENT.md 模板：

```markdown
# 当前开发进度（滚动日志）

> 本周/本月开发进度记录 - AI 了解最近完成了什么

**本周时间**: ${NEW_WEEK_START} - ${NEW_WEEK_END}（第 ${CURRENT_WEEK_NUM} 周）
**最后更新**: ${CURRENT_DATE} ${CURRENT_TIME}
**当前阶段**: [从 CONTEXT.md 获取]

---

## 本周概览

**Week ${CURRENT_WEEK_NUM}**: ${NEW_WEEK_START} - ${NEW_WEEK_END}

**本周目标**：
- [ ] [目标 1]
- [ ] [目标 2]

**本周完成**：
- （待更新）

---

## Day-by-Day 开发日志

（新月份开始，待记录）

---

## 本周任务

### P0（Critical）
- [ ] [从 CONTEXT.md 迁移]

### P1（High）
- [ ] [从 CONTEXT.md 迁移]

### P2（Medium）
- [ ] [待添加]

---

## 技术亮点

（本月待记录）

---

## 遇到的问题与解决方案

（本月待记录）

---

## 下周计划

### 优先级 1
1. [任务 1]
2. [任务 2]

---

**更新频率**: 每次 /checkpoint 或 /end 自动更新
**归档机制**: 每月归档到 archive/YYYY-MM.md
```

## Step 2: 更新 CONTEXT.md

### 2.1 更新项目阶段
如果上月完成了某个 Phase，更新阶段信息。

### 2.2 更新代码统计（可选）
```bash
# 统计代码行数
find apps/ -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.java" -o -name "*.py" | xargs wc -l 2>/dev/null | tail -1
```

### 2.3 更新下月任务
从"优先级 2"提升到"优先级 1"

## Step 3: 审查所有文档（彻底）

### 3.1 文档清单检查

检查以下文档是否存在且有效：
- [ ] docs/ai-context/CONTEXT.md
- [ ] docs/ai-context/CURRENT.md
- [ ] docs/development/DEVELOPMENT.md
- [ ] docs/development/frontend/components.md
- [ ] docs/development/frontend/pages.md
- [ ] docs/development/frontend/troubleshooting.md
- [ ] docs/development/backend/api.md
- [ ] docs/development/backend/database.md
- [ ] docs/development/backend/troubleshooting.md
- [ ] docs/architecture/OVERVIEW.md
- [ ] docs/architecture/tech-stack.md
- [ ] docs/architecture/adr/README.md
- [ ] docs/project/vision.md
- [ ] docs/project/design.md
- [ ] docs/project/ROADMAP.md

### 3.2 tech-stack.md 版本检查

对比 tech-stack.md 与 package.json（或 pom.xml / requirements.txt）：
- 检查版本是否一致
- 标记需要更新的依赖

### 3.3 文档链接检查

检查文档中的内部链接是否有效。

## Step 4: 清理 archive 目录

```bash
# 列出归档文件
ls -la docs/ai-context/archive/

# 检查超过 6 个月的归档
```

如果有超过 6 个月的归档：
- 建议压缩或删除
- 或保留但不再日常引用

## Step 5: Token 成本总报告

```bash
echo "=== 月度 Token 报告 ==="
echo "CONTEXT.md: $(wc -l < docs/ai-context/CONTEXT.md) 行"
echo "CURRENT.md: $(wc -l < docs/ai-context/CURRENT.md) 行"
echo "归档文件数: $(ls docs/ai-context/archive/*.md 2>/dev/null | wc -l)"
```

## Step 6: Git 操作

```bash
git add docs/
git commit -m "$(cat <<'EOF'
docs: ${CURRENT_MONTH} 月度归档

## 归档内容
- 归档 ${LAST_MONTH} 月 CURRENT.md
- 创建 ${CURRENT_MONTH} 月新模板
- 更新 CONTEXT.md

## 文档审查
- 所有文档已检查
- tech-stack.md 版本已核对

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

根据参数决定是否推送（推荐 `--push`）。

## Step 7: 输出月报

```
## 📅 ${CURRENT_MONTH} 月度归档完成

**归档时间**: ${CURRENT_DATE} ${CURRENT_TIME}

---

### 归档操作
- [x] ${LAST_MONTH} 月 CURRENT.md → archive/${LAST_MONTH}.md
- [x] 创建 ${CURRENT_MONTH} 月新 CURRENT.md
- [x] 更新 CONTEXT.md

### 文档健康状态
| 检查项 | 状态 |
|--------|------|
| 核心文档完整性 | ✅ |
| tech-stack 版本一致性 | ✅ / ⚠️ 需更新 |
| 文档链接有效性 | ✅ |

### Token 统计
| 文档 | 行数 | 估算 Token |
|------|------|------------|
| CONTEXT.md | X 行 | ~X tokens |
| CURRENT.md | X 行 | ~X tokens |

### archive 状态
- 归档文件数: X 个
- 最早归档: YYYY-MM
- 建议清理: [是/否]

### 下月重点
1. [任务 1]
2. [任务 2]

---
新的一月，新的开始！🚀
```

</workflow>
```

---

## 7. /audit - 项目健康检查

> 文件路径: `.claude/commands/audit.md`
> **版本**: v2.0（增强版）- 新增深度文档同步审计

### 7.1 功能概述

`/audit` 是项目全面健康检查命令，支持 5 种审计模式：

| 参数 | 审计范围 | 耗时预估 | 适用场景 |
|------|----------|----------|----------|
| `--quick` | Git 状态 + 文档日期检查 | 1-2 分钟 | 每天/提交前 |
| 无参数 | 标准检查（代码 + 依赖 + 文档） | 5-8 分钟 | 每周常规 |
| `--full` | 完整检查（含构建测试） | 10-15 分钟 | 大版本后 |
| `--security` | 安全漏洞 + 敏感信息扫描 | 3-5 分钟 | 上线前 |
| `--docs` | 深度文档同步审计 | 5-10 分钟 | Phase 完成后 |

### 7.2 核心检查项

#### 代码质量检查
- TODO/FIXME 统计
- console.log 残留检查
- 前端构建检查
- 后端编译检查

#### 依赖健康检查
- 过时依赖统计（pnpm outdated）
- 安全漏洞扫描（pnpm audit）
- 版本一致性（package.json vs tech-stack.md）

#### 文档同步审计（v2.0 新增）

**过时内容检测**：
- CONTEXT.md 项目阶段与 ROADMAP.md 一致性
- vision.md "非目标"是否包含已实现功能
- OVERVIEW.md 架构描述是否过时

**重复内容检测**：
| 内容类型 | 检查位置 |
|----------|----------|
| 技术栈列表 | CONTEXT.md, tech-stack.md, OVERVIEW.md |
| 目录结构 | CONTEXT.md, DEVELOPMENT.md, OVERVIEW.md |
| API 端点 | CONTEXT.md, api.md |
| 功能列表 | CONTEXT.md, vision.md, ROADMAP.md |

**缺失内容检测**：
- 实际组件 vs 文档组件（components.md）
- 实际 Controller vs 文档 API（api.md）
- 实际 Store vs 文档列表（CONTEXT.md）

**日期检查**：
- 文档最后更新日期是否过旧（>7天警告）

**链接有效性**：
- 内部链接是否存在目标文件

### 7.3 审计报告格式

```markdown
# 📋 项目审计报告

**审计时间**: YYYY-MM-DD HH:MM
**审计模式**: [quick/标准/full/security/docs]

---

## 📊 总览

| 维度 | 状态 | 评分 |
|------|------|------|
| 代码质量 | ✅/⚠️/❌ | X/100 |
| 依赖健康 | ✅/⚠️/❌ | X/100 |
| 文档同步 | ✅/⚠️/❌ | X/100 |
| **综合评分** | - | **X/100** |

---

## 🔴 过时内容（需立即修复）
| 文件 | 问题 | 当前值 | 应改为 |
|------|------|--------|--------|
| ... | ... | ... | ... |

## 🟡 重复内容（建议优化）
| 内容 | 出现位置 | 建议 |
|------|----------|------|
| ... | ... | ... |

## 🟢 缺失内容（可选补充）
| 模块/功能 | 文档位置 | 优先级 |
|-----------|----------|--------|
| ... | ... | ... |

## 📅 日期过旧的文档
## 🔧 代码质量问题
## 📦 依赖问题
## 🎯 行动建议（优先级排序）
```

### 7.4 使用建议

```bash
# 快速检查（每天/提交前）
/audit --quick

# 标准检查（每周）
/audit

# 完整审计（大版本后）
/audit --full

# 深度文档审计（Phase 完成后）
/audit --docs

# 安全检查（上线前）
/audit --security
```

### 7.5 工作流程概述

由于 `/audit` 命令内容较长（400+ 行），请直接参考项目中的 `.claude/commands/audit.md` 文件。

**主要工作流程**：
1. **Step 0**: 获取基本信息（时间、项目、最近提交）
2. **Step 1**: 解析参数（确定审计范围）
3. **Step 2**: 项目结构探索（代码/文档统计）
4. **Step 3**: 代码质量检查（TODO/FIXME、console.log、编译）
5. **Step 4**: 依赖健康检查（过时、漏洞、版本一致性）
6. **Step 5**: 文档同步审计（核心 - 过时/重复/缺失检测）
7. **Step 6**: Slash Commands 检查
8. **Step 7**: 生成审计报告
9. **Step 8**: 执行优化（需用户确认后执行）
10. **Step 9**: 提交变更

### 7.6 检查清单

#### Quick 模式
- [ ] Git 是否有未提交的更改？
- [ ] CONTEXT.md 项目阶段是否正确？
- [ ] CURRENT.md 是否更新？
- [ ] 各文档日期是否过旧（>7天）？

#### 标准模式额外检查
- [ ] 前端依赖是否有过时版本？
- [ ] 后端是否能正常编译？
- [ ] 组件数量与文档是否一致？
- [ ] API 数量与文档是否一致？

#### Full 模式额外检查
- [ ] 前端构建是否成功？
- [ ] 后端构建是否成功？
- [ ] 所有测试是否通过？

#### Docs 模式深度检查
- [ ] 每个文档的每个章节是否准确？
- [ ] 所有代码示例是否可运行？
- [ ] 所有链接是否有效？
- [ ] 是否有遗漏的新功能？

#### Security 模式检查
- [ ] 是否有硬编码的密钥/密码？
- [ ] .env 是否在 .gitignore 中？
- [ ] 依赖是否有已知漏洞？
- [ ] API 是否有认证保护？

### 7.7 最佳实践

1. **每次完成 Phase 后**: `/audit --full`
2. **每周一次**: `/audit`
3. **每天提交前**: `/audit --quick`
4. **上线前**: `/audit --security`

**常见问题处理**：

**Q: 发现大量过时内容怎么办？**
A: 优先处理 CONTEXT.md 和 ROADMAP.md，这两个是 AI 上下文恢复的核心。

**Q: 重复内容如何决定保留哪个？**
A: 按专门性原则：技术栈保留 tech-stack.md，API 保留 api.md，通用信息保留 CONTEXT.md。

**Q: 审计太慢怎么办？**
A: 使用 `--quick` 模式，只检查最关键的同步问题。

---

## 8. /deep-audit - 全面深度审计

> 文件路径: `.claude/commands/deep-audit.md`

### 8.1 完整配置

```markdown
---
description: 全面深度审计，不放过任何文件和代码行，自动优化并提交
argument-hint: [--no-fix|--no-push]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite
---

<task>
执行全面深度审计：探索每个文件、每行代码，对比文档与代码实际状态，**自动修复所有问题并提交**。

**审计范围（不放过任何角落）**：
1. 代码结构 - 组件/页面/Hooks/样式/配置
2. 文档系统 - AI 上下文/开发文档/架构文档/项目文档
3. Slash Commands - 所有 .claude/commands/*.md 命令
4. 设计系统 - CSS 变量/字体/颜色/动画
5. 依赖健康 - package.json vs 文档记录
6. 冗余检测 - 重复文件/过时内容/空目录

**默认行为**：审计 → 修复 → 提交 → 推送
**参数说明**：
- `--no-fix`: 仅审计，不修复
- `--no-push`: 修复并提交，但不推送
</task>

<workflow>

## Step 0: 初始化审计任务

**创建任务清单**（使用 TodoWrite）：
```
1. [pending] 代码结构全面探索
2. [pending] 文档系统全面探索
3. [pending] Slash Commands 审计
4. [pending] 设计系统审计
5. [pending] 依赖健康审计
6. [pending] 对比分析并识别问题
7. [pending] 生成审计报告
8. [pending] 执行全部优化
9. [pending] 提交并推送变更
```

**获取当前时间**：
```bash
AUDIT_DATE=$(date +%Y-%m-%d)
AUDIT_TIME=$(date +%H:%M)
```

---

## Step 1: 代码结构全面探索（标记 in_progress）

### 1.1 组件目录完整扫描

**扫描所有组件子目录**：
```bash
echo "=== UI 组件 ===" && ls -la ${FE_PATH}/src/components/ui/
echo "=== 装饰组件 ===" && ls -la ${FE_PATH}/src/components/decorations/
echo "=== 布局组件 ===" && ls -la ${FE_PATH}/src/components/layout/
echo "=== 区块组件 ===" && ls -la ${FE_PATH}/src/components/sections/
```

**记录格式**：
```
实际组件列表:
├── UI (X 个): [组件名称列表]
├── 装饰 (X 个): [组件名称列表]
├── 布局 (X 个): [组件名称列表]
└── 区块 (X 个): [组件名称列表]
```

### 1.2 Feature/页面深度扫描

**对每个 Feature 进行递归扫描**：
```bash
for dir in ${FE_PATH}/src/features/*/; do
  echo "=== $(basename $dir) ==="
  find "$dir" -type f -name "*.jsx" -o -name "*.js" -o -name "*.css" | head -30
done
```

### 1.3 Hooks 完整扫描

```bash
ls -la ${FE_PATH}/src/hooks/
find ${FE_PATH}/src/features -name "use*.js" -o -name "use*.jsx"
```

### 1.4 样式系统扫描

```bash
ls -laR ${FE_PATH}/src/styles/
```

### 1.5 配置文件扫描

```bash
cat ${FE_PATH}/package.json
cat ${FE_PATH}/vite.config.js
```

---

## Step 2: 文档系统全面探索（标记 in_progress）

### 2.1 扫描所有文档文件

```bash
find . -name "*.md" -not -path "*/node_modules/*" -type f | sort
find . -name "*.md" -not -path "*/node_modules/*" -type f | wc -l
```

### 2.2 必须完整读取的核心文档

1. `docs/ai-context/CONTEXT.md` - 项目上下文（逐行检查）
2. `docs/ai-context/CURRENT.md` - 当前进度（逐行检查）
3. `docs/development/frontend/components.md` - 组件文档
4. `docs/development/frontend/pages.md` - 页面文档
5. `docs/architecture/tech-stack.md` - 技术栈详解
6. `docs/project/ROADMAP.md` - 路线图

---

## Step 3: Slash Commands 审计（标记 in_progress）

### 3.1 扫描所有命令文件

```bash
ls -la .claude/commands/
```

### 3.2 逐一检查每个命令

**检查项**：
```
命令: /[name]
├── 描述: [读取 description]
├── 参数: [读取 argument-hint]
├── 允许工具: [读取 allowed-tools]
├── 工作流完整性: [检查是否有遗漏步骤]
├── 文档引用准确性: [检查引用的文件路径是否存在]
└── 问题: [列出发现的问题]
```

---

## Step 4: 设计系统审计（标记 in_progress）

### 4.1 对比 CSS 变量与文档

```bash
grep -h "^  --" ${FE_PATH}/src/styles/variables/*.css | sort
```

### 4.2 检查字体系统

```bash
grep -A 5 "fonts.googleapis.com" ${FE_PATH}/index.html
grep "font-family" ${FE_PATH}/src/styles/variables/typography.css
```

---

## Step 5: 依赖健康审计（标记 in_progress）

```bash
cat ${FE_PATH}/package.json | grep -A 200 '"dependencies"' | head -100
cd ${FE_PATH} && ${PM} outdated 2>/dev/null || echo "跳过 outdated 检查"
```

---

## Step 6: 对比分析并识别问题（标记 in_progress）

**对比维度**：
- 代码中的组件 vs components.md 记录
- 代码中的页面结构 vs pages.md 记录
- package.json vs tech-stack.md
- 实际完成情况 vs CONTEXT.md/ROADMAP.md 记录
- 命令引用的文件 vs 实际存在的文件
- 实际 CSS 变量 vs 设计系统文档

**问题分类**：
```
P0 - 严重（立即修复）:
1. [问题描述]

P1 - 中等（今日修复）:
1. [问题描述]

P2 - 轻微（本周修复）:
1. [问题描述]
```

---

## Step 7: 生成审计报告（标记 in_progress）

**写入** `docs/reports/deep-audit-YYYY-MM-DD.md`

---

## Step 8: 执行全部优化（标记 in_progress）

**注意**：除非包含 `--no-fix` 参数，否则自动执行修复

- 更新 CONTEXT.md/CURRENT.md/ROADMAP.md
- 更新 components.md/pages.md/tech-stack.md
- 优化 Slash Commands
- 清理冗余文件

---

## Step 9: 提交并推送变更（标记 in_progress）

**注意**：除非包含 `--no-push` 参数，否则自动推送

```bash
git add .
git commit -m "docs: 全面深度审计与自动优化

审计范围:
- 代码结构: X 个文件
- 文档系统: X 个文件
- Slash Commands: X 个命令
- 设计系统: X 个变量

发现并修复:
- P0 严重问题: X 处
- P1 中等问题: X 处
- P2 轻微问题: X 处

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

---

## Step 10: 完成审计

**输出完成报告**：
```
═══════════════════════════════════════════════════════════
✅ 全面深度审计完成！
═══════════════════════════════════════════════════════════

📊 审计统计:
├── 扫描代码文件: X 个
├── 扫描文档文件: X 个
├── 审计 Slash Commands: X 个
├── 检查设计系统变量: X 个
└── 总计扫描: X 项

🔧 修复统计:
├── P0 严重问题: X 处 ✅ 已修复
├── P1 中等问题: X 处 ✅ 已修复
├── P2 轻微问题: X 处 ✅ 已修复
└── 总计修复: X 处

📝 生成报告: docs/reports/deep-audit-YYYY-MM-DD.md

⏰ 下次建议审计: 一周后或重大变更后
═══════════════════════════════════════════════════════════
```

</workflow>
```

> **注意**：上述为精简版本，完整版本约 800 行，包含更详细的扫描规则和记录格式。请根据项目需求调整路径变量（`${FE_PATH}`, `${PM}`）。

### 8.2 与 /audit 的区别

| 特性 | /audit | /deep-audit |
|------|--------|-------------|
| 审计深度 | 标准检查 | 不放过任何文件 |
| Slash Commands | 不检查 | 全面检查 frontmatter、描述、工具权限 |
| 设计系统 | 不检查 | CSS 变量审计、命名规范 |
| 依赖审计 | 基础检查 | package.json vs 实际使用深度对比 |
| 默认行为 | 仅报告 | 自动修复 + 推送 |
| 使用频率 | 每周 | 每个 Phase 完成后 |

### 8.3 使用建议

```bash
# 完整审计 + 自动修复 + 推送（推荐）
/deep-audit

# 仅审计，不修复（用于检查）
/deep-audit --no-fix

# 审计修复，不推送（本地验证）
/deep-audit --no-push
```

### 8.4 变量说明

在使用此命令时，需要根据项目调整以下变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `${FE_PATH}` | 前端应用路径 | `apps/frontend` |
| `${PM}` | 包管理器 | `pnpm`, `npm`, `yarn` |
| `${PM_RUN}` | 运行脚本命令 | `pnpm run`, `npm run` |

---

## 9. /fix - ESLint 自动修复

> 文件路径: `.claude/commands/fix.md`

### 9.1 完整配置

```markdown
---
description: ESLint 自动修复，一键修复可自动修复的代码问题
argument-hint: [--check|--staged]
allowed-tools: Bash(cd ${FE_PATH} && ${PM_RUN} lint:*), Bash(npx lint-staged:*)
---

<task>
执行 ESLint 自动修复，修复所有可自动修复的代码问题。
</task>

<workflow>

## Step 1: 解析参数

**参数说明**：
- 无参数：修复全部文件
- `--check`：仅检查，不修复
- `--staged`：仅修复已 staged 的文件

---

## Step 2: 执行修复/检查

### 默认模式（无参数）

```bash
cd ${FE_PATH} && ${PM_RUN} lint --fix
```

### 检查模式（--check）

```bash
cd ${FE_PATH} && ${PM_RUN} lint
```

### Staged 模式（--staged）

```bash
cd ${FE_PATH} && npx lint-staged
```

---

## Step 3: 输出报告

**报告格式**：

```
📊 ESLint 修复报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 模式: [修复/检查/Staged]

📈 结果:
  - Errors: X 个
  - Warnings: X 个

✅ 状态: [通过/有警告/有错误]

💡 剩余需手动修复的问题:
  [列出无法自动修复的问题，如有]
```

</workflow>

<examples>
## 使用示例

```bash
# 修复全部
/fix

# 仅检查，不修复
/fix --check

# 仅修复 staged 文件（commit 前使用）
/fix --staged
```
</examples>
```

### 9.2 参数说明

| 参数 | 说明 | 适用场景 |
|------|------|----------|
| 无参数 | 修复全部文件 | 日常开发 |
| `--check` | 仅检查，不修复 | CI/CD 或审查 |
| `--staged` | 仅修复已 staged 的文件 | commit 前使用 |

### 9.3 变量说明

根据项目调整以下变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `${FE_PATH}` | 前端应用路径 | `apps/frontend` |
| `${PM_RUN}` | 运行脚本命令 | `pnpm run`, `npm run`, `yarn` |

### 9.4 使用建议

```bash
# 日常开发：修复全部
/fix

# 提交前：只修复暂存文件
/fix --staged

# 检查代码质量（CI 使用）
/fix --check
```

### 9.5 与 /deep-audit 的关系

| 命令 | 用途 | ESLint 处理 |
|------|------|-------------|
| `/fix` | 快速修复代码规范 | 仅 ESLint |
| `/deep-audit` | 全面审计 | 包含 ESLint + 更多 |

**建议**：
- 日常开发使用 `/fix` 快速修复
- Phase 完成后使用 `/deep-audit` 全面审计

---

## 10. 安装说明

### 10.1 快速安装

```bash
# 1. 创建目录
mkdir -p .claude/commands

# 2. 创建命令文件
# 从本文档复制每个命令的内容到对应文件：
# - .claude/commands/start.md
# - .claude/commands/checkpoint.md
# - .claude/commands/end.md
# - .claude/commands/weekly.md
# - .claude/commands/monthly.md
# - .claude/commands/audit.md
# - .claude/commands/deep-audit.md
# - .claude/commands/fix.md
```

### 10.2 验证安装

在 Claude Code 中测试：

```bash
/start --full
```

应该看到 AI 读取文档并输出验证报告。

### 10.3 注意事项

1. **时间命令兼容性**
   - macOS 使用 `date -v` 语法
   - Linux 使用 `date -d` 语法
   - 命令中已标注两种写法

2. **包管理器检测**
   - 命令会自动检测 npm/yarn/pnpm/bun
   - 根据 lock 文件判断

3. **路径约定**
   - 前端应用：`apps/frontend/`
   - 后端应用：`apps/backend/`
   - 文档目录：`docs/`

---

**文档性质**: 通用配置参考（可跨项目复用）
**版本**: v2.3
**更新日期**: 2025-12-07
