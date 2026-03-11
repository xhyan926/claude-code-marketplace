# Changelog

## [2.0.0] - 2026-03-11

### Added
- 新增 `go-sdk-planner` 技能（任务规划和分解）
- 新增 `go-sdk-tracker` 技能（任务状态跟踪）
- 新增 `go-sdk-coordinator` 技能（技能协调和调用）
- 新增 `code-reviewer` 技能（代码审查，支持多轮审查循环）
- 新增 `doc-verifier` 技能（文档验证，验证示例代码可运行）
- 创建统一的技能实现框架（`skills/common/`）
- 创建共享模板库（`templates/common/`）
- 为所有技能添加评估用例（10 个技能，44 个评估用例）

### Changed
- 模板引擎升级为 Go template 语法
- 所有 `.md` 模板迁移为 `.go.tmpl` 格式
- 统一命名规范：所有技能使用 `SKILL.md`
- 占位符命名规范统一为英文点表示法

### Improved
- 错误处理机制重构，建立统一错误码体系
- 评估覆盖率从 16.7% 提升至 100%
- 模板重复度从 40-50% 降至 <20%

### Deprecated
- 旧的 `update_task_status.py` 脚本功能迁移至 `go-sdk-tracker`

## [1.2.0] - 2026-03-06

### Added
- 与 `/sdk-doc` skill 的自动集成
- API 变更跟踪功能

### Changed
- 改进任务分解策略
- 优化子任务模板

## [1.1.0] - 2026-03-01

### Added
- 新增 `go-sdk-fuzz` 技能（模糊测试）
- 新增 `go-sdk-perf` 技能（性能基准测试）
- 新增 `go-sdk-integration` 技能（集成测试）
- 新增 `sdk-doc` 技能（API 文档生成）

### Changed
- 更新 BDD 测试命名规范
- 添加 Go 模板语法支持

## [1.0.0] - 2026-02-20

### Added
- 初始版本发布
- `go-sdk-dev-task` 技能（任务分解和管理）
- `go-sdk-ut` 技能（单元测试指南）
