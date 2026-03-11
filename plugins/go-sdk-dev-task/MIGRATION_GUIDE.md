# v2.0.0 迁移指南

## 概述

本指南帮助用户从 v1.2.0 迁移到 v2.0.0。

## 主要变更

### 技能架构调整

#### 新增技能

- **`go-sdk-planner`** - 任务规划和分解（原 go-sdk-dev-task 的一部分）
- **`go-sdk-tracker`** - 任务状态跟踪（原 go-sdk-dev-task 的一部分）
- **`go-sdk-coordinator`** - 技能协调（新技能）
- **`code-reviewer`** - 代码审查（新技能）
- **`doc-verifier`** - 文档验证（新技能）

#### 保留技能

- **`go-sdk-dev-task`** - 任务分解和管理（兼容性入口）
- **`go-sdk-ut`** - 单元测试指南
- **`go-sdk-fuzz`** - 模糊测试
- **`go-sdk-perf`** - 性能基准测试
- **`go-sdk-integration`** - 端到端集成测试
- **`sdk-doc`** - API 文档生成

### 模板系统升级

#### 模板语法变更

**旧语法 (v1.2.0)**：
```markdown
# {{ TASK_ID }} - {{ TASK_NAME }}
{{ 描述本子任务要达到的具体目标 }}
```

**新语法 (v2.0.0)**：
```markdown
# {{ .TaskID }} - {{ .TaskName }}
{{ .Description }}
```

#### 占位符命名规范

| 旧命名 | 新命名 |
|--------|--------|
| `{{ TASK_ID }}` | `{{ .TaskID }}`` |
| `{{ TASK_NAME }}` | `{{ .TaskName }}`` |
| `{{ X 天 }}` | `{{ .EstimatedDays }}`` |
| `{{ 描述 }}` | `{{ .Description }}`` |
| `{{ 步骤 }}` | `{{ .Steps }}`` |

#### 模板文件变更

- 所有 `.md` 模板文件已重命名为 `.go.tmpl`
- 模板引擎升级为 Go template 语法（使用 jinja2 实现）

### 命名规范统一

#### 文件命名

- 所有 `skill.md` 已重命名为 `SKILL.md`
- 影响的技能：go-sdk-fuzz, go-sdk-perf, go-sdk-integration, sdk-doc

## 新开发工作流

### v1.2.0 工作流

```
/go-sdk-dev-task → 开发实现 → /go-sdk-ut → 测试通过 → /sdk-doc
```

### v2.0.0 工作流

```
/go-sdk-planner → /go-sdk-tracker → 开发实现 → /go-sdk-ut
       ↓                    ↓
   生成子任务            更新状态
       ↓                    ↓
   开始开发            检测到 completed
       ↓                    ↓
   更新状态            触发 /code-reviewer
       ↓                    ↓
   代码完成              多轮审查循环
       ↓                    ↓
   审查通过              触发 /doc-verifier
       ↓                    ↓
   文档生成              验证文档
       ↓                    ↓
   验证通过              进入下一子任务
```

## 使用方式变更

### 任务规划

**v1.2.0**：
```bash
/go-sdk-dev-task "为 ObsClient 添加批量删除对象功能"
```

**v2.0.0**：
```bash
/go-sdk-planner "为 ObsClient 添加批量删除对象功能"
```

### 状态更新

**v1.2.0**：
```bash
python ~/.claude/plugins/skills/go-sdk-dev-task/scripts/update_task_status.py \
    --task-path subtasks/task-01 \
    --status completed
```

**v2.0.0**：
```bash
python ~/.claude/plugins/skills/go-sdk-tracker/scripts/tracker.py \
    --task-path subtasks/task-01 \
    --status completed
```

### 自动触发机制

**v2.0.0 新增**：

无需手动触发，coordinator 技能会根据 STATUS 文件自动触发相应技能：

1. 任务变为 `completed` → 自动触发 `/code-reviewer`
2. 审查通过 → 自动触发 `/doc-verifier`
3. 文档验证通过 → 自动进入下一子任务

### 代码审查

**v2.0.0 新增**：

```bash
# 在单元测试完成后自动触发
/code-reviewer
```

**多轮审查循环**：
1. 第一轮审查 → 生成 `REVIEW_COMMENTS.md`
2. 开发者修复问题 → 更新 `REVIEW_COMMENTS.md`
3. 第二轮审查 → 检查修复是否完整
4. 重复直到达成一致

### 文档验证

**v2.0.0 新增**：

```bash
# 在文档生成后自动触发
/doc-verifier
```

**验证内容**：
1. 文档完整性
2. 格式规范
3. 示例代码编译
4. 示例代码运行
5. API 一致性

## 兼容性说明

### 向后兼容

- **`/go-sdk-dev-task`** 技能仍然可用，作为兼容性入口
- 原有工作流仍然可以正常工作

### 需要适应的变化

1. **使用新技能**：推荐使用拆分后的独立技能
2. **更新模板**：现有自定义模板需要更新为 Go template 语法
3. **利用自动触发**：新工作流支持技能自动触发，减少手动操作

## 迁移步骤

### 第 1 步：更新插件

```bash
# 重新安装插件
/plugin install go-sdk-dev-task@claude-code-marketplace

# 重启 Claude Code
```

### 第 2 步：更新模板（如适用）

如果使用了自定义模板：

1. 将占位符更新为英文点表示法
2. 使用 Go template 语法（`{{ if }}`、`{{ range }}`）
3. 将文件重命名为 `.go.tmpl`

### 第 3 步：更新工作流

1. 使用 `/go-sdk-planner` 替代 `/go-sdk-dev-task` 进行任务规划
2. 依赖 `/code-reviewer` 和 `/doc-verifier` 进行质量和文档验证
3. 利用自动触发机制减少手动操作

### 第 4 步：验证迁移

1. 运行新技能的评估用例：
   ```bash
   /skill-creator run-evals skills/go-sdk-planner/evals/evals.json
   ```

2. 测试完整的开发工作流

## 常见问题

### Q1: 旧的 `/go-sdk-dev-task` 还能用吗？

A: 可以的，作为兼容性入口仍然保留。但推荐使用新的独立技能。

### Q2: 如何使用新的自动触发机制？

A: 无需额外配置，coordinator 技能会根据 STATUS 文件自动触发。需要确保：
   - `.claude-plugin/hooks.json` 配置正确
   - STATUS 文件路径正确

### Q3: 模板语法有什么变化？

A: 主要变化：
   - 占位符使用英文点表示法：`{{ .VariableName }}`
   - 支持条件渲染：`{{ if .Condition }}...{{ end }}`
   - 支持循环：`{{ range .Items }}...{{ end }}`

### Q4: 如何贡献新的技能或模板？

A: 请参阅 `CONTRIBUTING.md` 了解贡献流程。

## 支持和帮助

- 查看 `CLAUDE.md` 了解项目约定
- 查看 `README.md` 了解插件使用
- 查看 `CHANGELOG.md` 了解变更历史
- 提交 [Issue](https://github.com/xhyan926/claude-code-marketplace/issues) 报告问题

## 版本对比

| 功能 | v1.2.0 | v2.0.0 |
|------|----------|----------|
| 技能数量 | 6 | 10 |
| 技能实现 | 1/6 (16.7%) | 10/10 (100%) |
| 评估覆盖率 | 16.7% | 100% |
| 模板重复度 | 40-50% | <20% |
| 命名规范 | 不统一 | 统一 |
| 自动触发 | 否 | 是 |
| 代码审查 | 无 | 有（多轮循环） |
| 文档验证 | 无 | 有 |

---

**版本**: 2.0.0
**发布日期**: 2026-03-11
