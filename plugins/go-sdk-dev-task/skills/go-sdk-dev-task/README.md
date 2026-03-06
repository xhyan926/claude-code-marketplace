# go-sdk-dev-task Plugin

华为云 OBS Go SDK 开发任务分解技能。

## 技能说明

`go-sdk-dev-task` 技能用于将 OBS SDK Go 开发任务分解为可独立完成、可追踪、具有幂等性的子任务，并在每个子任务完成后自动生成对应的 API 文档。

## 功能特性

- 标准化任务分解
- 完整的子任务模板
- 与 /go-sdk-ut skill 集成（测试阶段）
- 与 /sdk-doc skill 集成（文档自动生成）
- 幂等性保证
- 验收报告生成
- API 变更跟踪
- 文档质量验证

## 使用方法

在对话中使用技能会自动触发：

```
"我需要开发一个新的 OBS 功能，怎么分解这个任务？"
"帮我规划一下这个重构任务"
```

详细使用示例请参阅 `skills/go-sdk-dev-task/USAGE_EXAMPLES.md`。

## 版本

1.2.0 (2026-03-06)

### 更新内容
- 新增与 /sdk-doc skill 的自动集成
- 添加 API 变更跟踪模板 (API_CHANGE_TRACKER.md)
- 子任务完成后自动生成接口文档
- 增强文档质量验证流程
- 完善文档生成检查清单

## 许可证

MIT License
