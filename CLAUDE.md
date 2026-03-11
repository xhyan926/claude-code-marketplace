# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Claude Code 插件市场项目，专门为华为云 OBS SDK Go 开发提供任务管理、测试和文档生成工具链。项目采用技能（Skill）架构，每个技能独立负责特定功能，并可通过组合实现完整的开发工作流。

## 插件安装

```bash
# 添加插件市场源
/plugin marketplace add https://github.com/xhyan926/claude-code-marketplace.git

# 安装 go-sdk-dev-task 插件（重启后生效）
/plugin install go-sdk-dev-task@claude-code-marketplace
```

## 核心技能

### 任务管理

- **`/go-sdk-dev-task`** - 将复杂开发任务分解为 1-3 天可完成的子任务，支持幂等性和进度追踪。每个子任务完成后自动调用 `/sdk-doc` 生成文档。

### 测试技能

- **`/go-sdk-ut`** - 单元测试编写指南，支持 BDD 风格测试命名
- **`/go-sdk-fuzz`** - 模糊测试，针对 XML 解析、URL 构建、签名验证等敏感功能
- **`/go-sdk-perf`** - 性能基准测试，提供标准模板
- **`/go-sdk-integration`** - 端到端集成测试

### 文档生成

- **`/sdk-doc`** - API 接口文档自动生成，提供标准化模板和质量检查清单

## 技能工作流

典型开发流程：
```
/go-sdk-dev-task → 代码实现 → /go-sdk-ut → /go-sdk-fuzz → /go-sdk-perf → /go-sdk-integration → /sdk-doc
```

`go-sdk-dev-task` 会自动在子任务完成后调用 `/sdk-doc`，实现文档自动生成。

## 目录结构

```
.claude-plugin/marketplace.json    # 插件市场索引文件
plugins/
  go-sdk-dev-task/                  # 主插件
    .claude-plugin/plugin.json      # 插件定义
    skills/
      go-sdk-dev-task/              # 任务分解技能
      go-sdk-ut/                    # 单元测试技能
      go-sdk-fuzz/                  # 模糊测试技能
      go-sdk-perf/                  # 性能测试技能
      go-sdk-integration/           # 集成测试技能
      sdk-doc/                      # 文档生成技能
        templates/                   # 文档模板
```

## 模板系统

所有技能都使用模板系统确保输出一致性：

- `implementation_template.md` - 实施计划模板
- `test_plan_template.md` - 测试计划模板
- `api_change_tracker.md` - API 变更跟踪
- `fuzz_test.go.tmpl` - 模糊测试代码模板
- `benchmark_test.go.tmpl` - 基准测试代码模板

模板使用 `{{ VARIABLE }}` 占位符，使用时替换为实际值。

## 状态管理

`go-sdk-dev-task` 通过 `STATUS` 文件管理子任务进度，支持幂等操作。状态文件格式：

```
子任务名称: pending | in_progress | completed | blocked
```

## 评估系统

技能包含评估用例，位于 `skills/*/evals/evals.json`，用于验证功能正确性。

## 设计原则

1. **模块化** - 每个技能职责单一，可独立使用
2. **可组合** - 技能间可相互调用和协调
3. **模板化** - 使用模板确保输出一致性
4. **自动化** - 从任务分解到文档生成全流程自动化
5. **标准化** - 遵循 Go 项目开发规范

## 适用场景

专为华为云 OBS SDK Go 项目设计，适用于需要系统性规划的复杂开发工作，包括新功能开发、Bug 修复和代码重构。
