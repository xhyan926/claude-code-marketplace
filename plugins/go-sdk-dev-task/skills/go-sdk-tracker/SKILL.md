---
name: go-sdk-tracker
description: 任务状态跟踪技能，用于管理子任务状态、进度跟踪和依赖检查，通过 STATUS 文件和 SUBTASKS.md 维护任务进度。
---

# go-sdk-tracker

## 技能用途

本技能用于跟踪和管理子任务的状态。支持：

- 状态更新（pending/in_progress/completed/blocked）
- 进度跟踪
- 依赖检查
- SUBTASKS.md 更新
- 幂等性保证

## 前置条件

1. **子任务目录存在**：`subtasks/task-XX/` 目录已创建
2. **必需文件存在**：TASK.md、IMPLEMENTATION.md、TEST_PLAN.md

## 使用方法

### 状态更新
```bash
python scripts/tracker.py --task-path subtasks/task-01 --status completed
```

### 查看状态
```bash
cat subtasks/task-01/STATUS
```

## 状态定义

| 状态 | 说明 | 触发条件 |
|------|------|----------|
| pending | 等待开始 | 子任务创建后 |
| in_progress | 进行中 | 开始开发后 |
| completed | 已完成 | 所有验收标准满足后 |
| blocked | 被阻塞 | 前置依赖未完成 |

## 验证规则

### 完成状态验证
当状态设置为 `completed` 时，执行以下验证：

1. **文件完整性检查**：
   - TASK.md 存在
   - IMPLEMENTATION.md 存在
   - TEST_PLAN.md 存在
   - STATUS 存在

2. **依赖检查**：
   - 前置子任务状态为 completed

### 状态转换规则

| 当前状态 | 可转换状态 | 限制 |
|----------|-----------|------|
| pending | in_progress | 无 |
| in_progress | completed, blocked | 需验证文件完整性 |
| completed | - | 不允许回退 |
| blocked | in_progress | 依赖完成后 |

## SUBTASKS.md 更新

当子任务状态变化时，自动更新 SUBTASKS.md：

```markdown
## 总体进度
- [x] 子任务 1 - 已完成
- [ ] 子任务 2 - 进行中
- [ ] 子任务 3 - 待开始
```

## 幂等性保证

1. **状态更新幂等**：
   - 重复设置相同状态不会产生错误
   - STATUS 文件不会被重复修改

2. **SUBTASKS.md 更新幂等**：
   - 只更新对应子任务的复选框
   - 不会影响其他子任务

## 依赖检查

### 检查前置依赖
```python
# 检查 task-02 的前置依赖
if not is_dependency_completed('task-01'):
    raise DependencyError("前置任务 task-01 未完成")
```

### 检查阻塞关系
```python
# 检查当前任务是否阻塞其他任务
blocking_tasks = get_blocking_tasks('task-01')
if blocking_tasks and status == 'completed':
    notify_blocking_tasks(blocking_tasks)
```

## 错误处理

### 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| FileNotFoundError | 子任务目录不存在 | 检查路径是否正确 |
| ValidationError | 文件验证失败 | 确保所有必需文件存在 |
| DependencyError | 前置依赖未完成 | 先完成前置任务 |

## Hook 集成

本技能通过 Hook 与其他技能集成：

### on_status_changed
当 STATUS 文件变化时触发：
- 更新 SUBTASKS.md
- 通知依赖此任务的其他任务

### on_task_completed
当状态变为 completed 时触发：
- 验证文件完整性
- 检查是否需要触发其他技能
- 通知 coordinator 技能
