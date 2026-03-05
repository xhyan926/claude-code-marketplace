---
name: go-sdk-dev-task
description: 分解 OBS SDK Go 开发任务为可独立完成、可追踪、具有幂等性的子任务。当用户需要在华为云 OBS Go SDK 中开发新功能、修复 Bug 或重构代码时使用此技能。适用于需要将复杂开发任务拆分为 1-3 天可完成的子任务的场景，特别是涉及 API 开发、测试用例编写和代码质量检查的工作。即使任务看起来简单，如果涉及多步骤开发流程、需要遵循项目约定或需要系统性规划，都应该使用此技能。用户提到"任务分解"、"任务规划"、"拆分任务"、"子任务"、"开发流程"、"需要规划"、"如何组织"、"怎么安排"时，都应该触发此技能。当任务涉及新功能开发、API实现、Bug修复、代码重构、性能优化或需要系统性规划的开发工作时，使用此技能。不要为简单的单元测试编写、代码格式化、文档查询或单个文件修改等简单任务触发此技能。
---

# go-sdk-dev-task

## 技能用途

本技能用于将 OBS SDK Go 开发任务分解为可独立完成、可追踪、具有幂等性的子任务。适用于：

- 新功能开发（如添加新的 API 方法）
- Bug 修复（如内存泄漏、逻辑错误）
- 代码重构（如提取公共逻辑、优化性能）
- 性能优化（如减少内存使用、提高响应速度）
- 文档更新（如补充示例、修改注释）

## 前置条件

在使用此技能前，确保：

1. **项目环境正确**：工作目录为 `/Users/xhyan/project/SDKS/huaweicloud-sdk-go-obs`
2. **需求明确**：用户提供了清晰的功能需求、Bug 描述或重构目标
3. **上下文充分**：已阅读相关代码文件，理解现有架构和约定

## 输入格式

用户提供以下信息之一：

### 功能开发
```
"为 ObsClient 添加批量删除对象功能"
```

### Bug 修复
```
"修复 PutObject 在大文件上传时的内存泄漏"
```

### 代码重构
```
"重构 auth.go 中的签名逻辑"
```

## 输出格式

技能生成以下文件：

### 1. 主任务文件：`SUBTASKS.md`
```markdown
# 任务名称

## 任务描述
详细说明任务目标和范围

## 子任务列表
1. 子任务 1 - 设计阶段
2. 子任务 2 - 实现阶段
3. 子任务 3 - 测试阶段
4. 子任务 4 - 验收阶段

## 总体进度
[ ] 子任务 1
[ ] 子任务 2
[ ] 子任务 3
[ ] 子任务 4
```

### 2. 子任务目录：`subtasks/task-01/`
每个子任务包含：
- `TASK.md` - 子任务详细描述（使用 `templates/subtask_template.md`）
- `STATUS` - 状态标记（pending/in_progress/completed）
- `IMPLEMENTATION.md` - 实施计划（使用 `templates/implementation_template.md`）
- `TEST_PLAN.md` - 测试计划（使用 `templates/test_plan_template.md`）

### 3. 验收报告：`ACCEPTANCE_REPORT.md`
子任务完成后生成，包含：
- 完成情况总结
- 测试结果详情
- 代码质量检查
- 样例运行结果

**注意**：可以使用 `templates/acceptance_report_simple.md` 生成简化版验收报告以提高效率

## 任务分解原则

### 粒度控制
- 每个子任务应在 **1-3 天** 内完成
- 避免过度拆分（<1 天）或过度聚合（>3 天）
- 考虑开发、测试、验证的完整流程

### 幂等性保证
使用 **双重检查机制**：

1. **文件检查**：检查关键文件是否存在
   ```go
   // 示例：检查 API 方法是否存在
   if exists("obs/client_object.go", "func (cli *ObsClient) BatchDeleteObjects") {
       // 文件已存在，跳过创建
   }
   ```

2. **状态标记**：通过 STATUS 文件标记执行状态
   ```
   subtasks/task-01/STATUS: completed
   ```

### 依赖管理
- 子任务之间应保持最小依赖
- 必须依赖时，在 TASK.md 中明确说明
- 使用阻塞标记确保执行顺序

## 子任务模板

### TASK.md 结构

```markdown
# 子任务编号：设计阶段

## 目标
具体描述本子任务要达到的目标

## 范围
- 包含内容
- 不包含内容

## 依赖
- 前置子任务：task-00（如果有）
- 阻塞：task-02, task-03（如果有）

## 实施步骤
1. 分析需求，理解业务场景
2. 设计 API 接口和数据结构
3. 编写设计文档

## 验收标准
- [ ] API 设计文档完成
- [ ] 数据结构定义清晰
- [ ] 与现有架构兼容

## 状态
pending / in_progress / completed
```

## 幂等性实现

### 检查机制
在执行每个子任务前，运行以下检查：

1. **状态检查**：读取 `STATUS` 文件
   - 如果文件不存在：状态为 pending
   - 如果内容为 completed：验证文件完整性后跳过
   - 其他状态：继续执行

2. **文件完整性验证**：确认必需文件存在
   - TASK.md：任务描述
   - IMPLEMENTATION.md：实施计划
   - TEST_PLAN.md：测试计划

### 状态更新
更新 STATUS 文件：

```bash
echo "completed" > subtasks/task-01/STATUS
```

或使用脚本 `scripts/update_task_status.py` 更新状态：

```bash
python ~/.claude/plugins/skills/go-sdk-dev-task/scripts/update_task_status.py \
    --task-path subtasks/task-01 \
    --status completed
```

## 验收报告生成

子任务完成后，生成验收报告 `ACCEPTANCE_REPORT.md`：

```markdown
# 子任务验收报告

## 完成情况总结
- 实现了 XXX 功能
- 解决了 XXX 问题
- 优化了 XXX 性能

## 测试结果详情
### 单元测试
- 测试用例总数：X
- 通过率：100%
- 覆盖率：85%

### 集成测试
- 场景 1：✓ 通过
- 场景 2：✓ 通过

## 代码质量检查
- [ ] 符合 Go 代码规范
- [ ] 通过 golint 检查
- [ ] 无内存泄漏
- [ ] 错误处理完善

## 样例运行结果
```
示例代码运行正常，输出符合预期
```

## 改进建议
（如有）
```

## 与 /go-sdk-ut skill 集成

### 测试阶段必须调用
在子任务的测试阶段，**必须明确调用** `/go-sdk-ut` skill：

```markdown
## 测试阶段
1. 使用 /go-sdk-ut skill 编写单元测试
   - 测试命名：Should_ExpectedResult_When_Condition_Given_State
   - 使用 testify 进行断言
   - 使用 httptest 模拟 HTTP 服务器
   - 使用 gomonkey 进行 mock
2. 运行测试：`go test ./... -v`
3. 检查覆盖率：`go test ./... -cover`
```

### 集成检查点
在子任务验收报告中，必须包含：

```markdown
## 测试结果
- 是否调用 /go-sdk-ut skill：是
- 测试用例数量：X
- 测试覆盖率：X%
- 所有测试是否通过：是/否
```

## 执行流程

### 第一阶段：需求分析
1. 与用户确认任务需求
2. 识别关键依赖和约束
3. 确定任务类型（新功能/Bug/重构）

### 第二阶段：任务分解
1. 根据任务类型应用相应的分解策略
2. 创建 SUBTASKS.md（包含任务描述、子任务列表、总体进度）
3. 为每个子任务创建目录，并确保包含以下所有文件：
   - `TASK.md` - 子任务详细描述（目标、范围、依赖、实施步骤、验收标准）
   - `IMPLEMENTATION.md` - 实施计划（详细步骤、技术细节、时间估算）
   - `TEST_PLAN.md` - 测试计划（测试用例、测试工具、验收标准）
   - `STATUS` - 状态标记文件（内容为 pending/in_progress/completed）
4. 验证每个子任务目录的完整性，确保所有必需文件都已创建

### 第三阶段：子任务执行
1. 按顺序执行子任务
2. 执行前检查状态和文件：
   - 读取子任务的 STATUS 文件
   - 如果状态为 completed，验证 TASK.md、IMPLEMENTATION.md、TEST_PLAN.md 是否存在
   - 如果验证通过，跳过该子任务；否则标记为 needs_rerun
3. 执行子任务内容，确保所有必需文件都正确生成
4. 执行后更新状态文件
5. 生成验收报告（使用 templates/acceptance_report_template.md）

### 第四阶段：总体验收
1. 汇总所有子任务的验收报告
2. 运行完整的测试套件
3. 确认所有约定遵循

## 注意事项

### 项目约定参考
根据 `CLAUDE.md`，遵循以下约定：

1. **测试命名规范**：使用 BDD 风格
   ```
   Should_return_error_When_invalid_input_Given_empty_string
   ```

2. **测试工具**：
   - testify - 断言库
   - httptest - HTTP 服务器模拟
   - gomonkey - Mock 工具

3. **测试质量原则**：
   - 合并重复测试用例
   - 优先关注功能逻辑
   - 确保业务价值明确

4. **架构层次**：
   - 客户端方法：`client_*.go`
   - 特性层：`trait_*.go`
   - HTTP 层：`http.go`, `auth*.go`
   - 模型层：`model_*.go`

5. **扩展系统**：使用函数式选项模式
   - `WithXXX()` 函数

### 常见陷阱

1. **过度设计**：避免为简单任务创建过多子任务
2. **状态不一致**：确保 STATUS 文件与实际状态同步
3. **测试缺失**：每个子任务都必须有对应的测试
4. **文档滞后**：代码变更后及时更新文档

### 质量检查清单

每个子任务完成后，检查：

- [ ] 代码通过所有测试
- [ ] 测试覆盖率达标（建议 >80%）
- [ ] 符合 Go 代码规范
- [ ] 无明显的性能问题
- [ ] 错误处理完善
- [ ] 文档已更新
- [ ] 示例代码可运行

## 模板文件

技能包含以下模板文件，位于 `templates/` 目录：

- `subtask_template.md` - 子任务 TASK.md 标准模板
- `implementation_template.md` - 子任务 IMPLEMENTATION.md 实施计划模板
- `acceptance_report_template.md` - 验收报告详细模板
- `acceptance_report_simple.md` - 验收报告简化模板（推荐用于提高效率）
- `test_plan_template.md` - 测试计划模板

在创建新子任务时，必须使用这些模板确保一致性：
1. 读取相应的模板文件
2. 替换占位符（{{ TASK_NAME }} 等）
3. 保存到对应的子任务目录
4. 确保所有四个必需文件都已创建
5. 验收报告可以使用简化版模板提高效率

## 参考资源

- 项目文档：`CLAUDE.md`
- 测试指南：使用 `/go-sdk-ut` skill
- Go 测试最佳实践：https://go.dev/doc/tutorial/add-a-test
- BDD 测试模式：https://martinfowler.com/bliki/GivenWhenThen.html

## 执行效率优化

为了提高技能执行效率，遵循以下原则：

1. **最小化文件生成**：
   - 只创建必需的文件（SUBTASKS.md、子任务文件）
   - 避免创建冗余的文档
   - 每个子任务只包含核心文件：TASK.md、IMPLEMENTATION.md、TEST_PLAN.md、STATUS

2. **快速任务分解**：
   - 根据任务类型快速应用标准分解模板
   - 不要过度分析或重复阅读相同文件
   - 直接使用模板创建文件，避免逐字复制

3. **批量文件操作**：
   - 一次性创建所有子任务目录和文件
   - 避免多次文件系统操作
   - 使用简化的文件内容，减少输出时间

4. **智能状态判断**：
   - 只在需要时才创建子任务文件
   - 对于分析阶段的子任务，可以简化内容
   - 避免为所有子任务生成完整的内容

5. **优化输出质量**：
   - 优先保证核心信息完整（目标、步骤、验收标准）
   - 简化技术细节，避免冗长
   - 使用简洁的描述，避免重复
