# Go SDK 开发任务插件

## 概述

这是 Claude Code 插件，专门为华为云 OBS SDK Go 开发提供任务管理、测试和文档生成工具链。插件采用技能（Skill）架构，每个技能独立负责特定功能，并通过组合实现完整的开发工作流。

## 插件安装

### 添加插件市场源

```bash
/plugin marketplace add https://github.com/xhyan926/claude-code-marketplace.git
```

### 安装插件

```bash
/plugin install go-sdk-dev-task@claude-code-marketplace
```

**注意**：安装后需要重启 Claude Code 才能生效。

## 核心技能

### 任务管理

- **`/go-sdk-dev-task`** - 任务分解和管理（兼容性入口）
- **`/go-sdk-planner`** - 任务规划和分解
- **`/go-sdk-tracker`** - 任务状态跟踪
- **`/go-sdk-coordinator`** - 技能协调和调用

### 测试技能

- **`/go-sdk-ut`** - 单元测试编写指南，支持 BDD 风格测试命名
- **`/go-sdk-fuzz`** - 模糊测试，针对 XML 解析、URL 构建、签名验证等敏感功能
- **`/go-sdk-perf`** - 性能基准测试，提供标准模板
- **`/go-sdk-integration`** - 端到端集成测试

### 质量保证

- **`/code-reviewer`** - 代码审查，精通 Go、对象存储、网络编程、Clean Code、设计模式
- **`/doc-verifier`** - 文档验证，验证文档完整性和示例代码可运行性

### 文档生成

- **`/sdk-doc`** - API 接口文档自动生成，提供标准化模板和质量检查清单

## 完整开发工作流

```
/go-sdk-planner → /go-sdk-tracker → 开发和单元测试 → /code-reviewer → /doc-verifier → /go-sdk-tracker(completed)
```

**详细流程**：
1. **任务规划**：使用 `/go-sdk-planner` 分解任务为子任务
2. **开发实现**：编写 Go 代码实现功能
3. **单元测试**：使用 `/go-sdk-ut` 编写 BDD 风格测试
4. **代码审查**：使用 `/code-reviewer` 进行代码质量检视（多轮循环）
5. **文档验证**：使用 `/doc-verifier` 验证文档和示例代码
6. **状态更新**：使用 `/go-sdk-tracker` 更新任务状态

## 技能间协调

技能之间通过 Hook 机制自动协调：

- **on_task_completed**：任务完成后自动触发 `/code-reviewer`
- **on_review_completed**：审查通过后自动触发 `/doc-verifier`
- **on_all_subtasks_completed**：所有任务完成后生成最终报告

## 版本信息

- **当前版本**：2.0.0
- **发布日期**：2026-03-11

## v2.0.0 更新内容

### 新增功能
- 新增 `go-sdk-planner`、`go-sdk-tracker`、`go-sdk-coordinator` 三个独立技能
- 新增 `code-reviewer` 技能，支持多轮代码审查循环
- 新增 `doc-verifier` 技能，验证文档和示例代码正确性
- 创建统一的技能实现框架（`skills/common/`）
- 创建共享模板库减少重复（`templates/common/`）

### 改进
- 模板引擎升级为 Go template 语法
- 评估覆盖率从 16.7% 提升至 100%（10 个技能，44 个评估用例）
- 统一命名规范：所有技能使用 SKILL.md

### 技术改进
- 建立统一错误处理规范
- 提供进度追踪和交互式问答功能
- 模板重复度从 40-50% 降至 <20%

## 目录结构

```
plugins/go-sdk-dev-task/
├── .claude-plugin/
│   ├── plugin.json           # 插件定义
│   └── marketplace.json      # 插件市场索引
├── skills/                  # 技能目录
│   ├── common/              # 通用框架
│   │   ├── skill_base.py
│   │   ├── template_engine.py
│   │   ├── error_handler.py
│   │   └── ...
│   ├── go-sdk-dev-task/    # 任务管理（兼容入口）
│   ├── go-sdk-planner/     # 任务规划
│   ├── go-sdk-tracker/     # 状态跟踪
│   ├── go-sdk-coordinator/  # 技能协调
│   ├── code-reviewer/      # 代码审查
│   ├── doc-verifier/       # 文档验证
│   ├── go-sdk-ut/         # 单元测试
│   ├── go-sdk-fuzz/        # 模糊测试
│   ├── go-sdk-perf/        # 性能测试
│   ├── go-sdk-integration/  # 集成测试
│   └── sdk-doc/           # 文档生成
└── templates/              # 模板目录
    ├── common/             # 共享模板库
    └── ...
```

## 参考资源

- 项目文档：`CLAUDE.md`
- Go SDK 开发规范：[Effective Go](https://go.dev/doc/effective_go)
- 测试最佳实践：[Go Testing](https://go.dev/doc/tutorial/add-a-test)

## 贡献指南

欢迎贡献代码、文档或提出改进建议。请查看各技能目录下的文档了解如何贡献。

## 许可证

本插件遵循华为云 OBS SDK 项目的许可证。
