# v2.0.0 快速入门

## 概述

本文档帮助快速开始使用 v2.0.0 版本的 Go SDK 开发任务技能系统。

## 立即开始

### 1. 重启 Claude Code

确保加载新的插件版本：

```bash
# 重启 Claude Code 应用
```

### 2. 验证插件加载

```bash
# 检查插件版本
cat ~/.claude/plugins/go-sdk-dev-task/.claude-plugin/plugin.json
```

预期输出包含：`"version": "2.0.0"`

### 3. 测试技能

#### 测试任务规划
```
/go-sdk-planner "为 ObsClient 添加批量删除对象功能"
```

#### 测试状态跟踪
```bash
# 查看 go-sdk-tracker 技能
cat plugins/go-sdk-dev-task/skills/go-sdk-tracker/SKILL.md
```

#### 测试代码审查
```
/code-reviewer
```

#### 测试文档验证
```
/doc-verifier
```

## 新工作流程

### 推荐工作流

```
1. /go-sdk-planner - 规划任务
   ↓
2. /go-sdk-tracker - 更新状态（完成时自动触发审查）
   ↓
3. 开发实现 + /go-sdk-ut - 单元测试
   ↓
4. /code-reviewer - 代码审查（多轮循环）
   ↓
5. /doc-verifier - 文档验证
   ↓
6. /go-sdk-tracker - 进入下一子任务
```

### 兼容性工作流

```
1. /go-sdk-dev-task - 完整任务管理（兼容 v1.x）
   ↓
2. 开发实现 + /go-sdk-ut - 单元测试
   ↓
3. /sdk-doc - 文档生成
```

## 技能对比

| 功能 | v1.2.0 | v2.0.0 |
|------|---------|---------|
| 任务分解 | go-sdk-dev-task | go-sdk-planner |
| 状态跟踪 | 内置 | go-sdk-tracker |
| 代码审查 | 无 | code-reviewer |
| 文档验证 | 无 | doc-verifier |
| 技能协调 | 无 | go-sdk-coordinator |
| 评估覆盖率 | 16.7% (1/6 技能) | 100% (10/10 技能) |

## 常见问题

### Q: 我需要安装 jinja2 吗？

A: 不需要。插件包含 `simple_template.py`，不需要外部依赖。`template_engine.py` 是高级功能，需要 jinja2 时会提示。

### Q: 如何使用新的代码审查功能？

A:
```
/code-reviewer
```
技能会自动检查代码，生成 `REVIEW_COMMENTS.md`，支持多轮审查循环。

### Q: 如何使用新的文档验证功能？

A:
```
/doc-verifier
```
技能会验证文档完整性，编译并运行示例代码，生成 `DOC_VERIFICATION.md`。

### Q: 我的旧工作流还能用吗？

A: 能的。`/go-sdk-dev-task` 仍然保留，保持向后兼容。

## 迁移到新技能

### 第 1 步：学习新技能

1. 阅读 `go-sdk-planner/SKILL.md`
2. 阅读 `go-sdk-tracker/SKILL.md`
3. 阅读 `code-reviewer/SKILL.md`
4. 阅读 `doc-verifier/SKILL.md`

### 第 2 步：尝试新流程

1. 使用 `/go-sdk-planner` 规划一个小任务
2. 按照"推荐工作流"执行
3. 对比新旧流程的差异

### 第 3 步：逐步迁移

1. 新项目使用新流程
2. 旧项目继续使用兼容流程
3. 积累经验后全面迁移

## 获取帮助

- 查看详细文档：
  - `MIGRATION_GUIDE.md` - 完整迁移指南
  - `VERIFICATION.md` - 验证清单
  - `CONTRIBUTING.md` - 贡献指南
  - `CHANGELOG.md` - 变更历史

- 查看各技能文档：
  - `skills/go-sdk-planner/SKILL.md`
  - `skills/code-reviewer/SKILL.md`
  - `skills/doc-verifier/SKILL.md`
  - 等等

## 功能亮点

### 自动触发机制

- 任务完成时自动触发代码审查
- 审查通过时自动触发文档验证
- 减少手动操作

### 多轮代码审查

- 支持开发-审查循环
- 直到达成一致
- 追踪每个问题的状态

### 文档验证

- 验证文档完整性
- 编译示例代码
- 运行示例代码
- 检查 API 一致性

### 共享模板库

- 减少模板重复 60%+
- 统一模板格式
- 提高维护性

---

**版本**: 2.0.0
**发布日期**: 2026-03-11
