---
name: go-sdk-coordinator
description: 技能协调技能，用于协调各个技能间的执行顺序，通过 Hook 机制实现自动触发，确保开发工作流程顺利进行。
---

# go-sdk-coordinator

## 技能用途

本技能用于协调各个开发技能的执行，确保工作流程按照预定顺序进行。主要功能：

- 监控任务状态变化
- 根据 STATUS 文件触发相应技能
- 协调开发、测试、文档生成等环节
- 维护整体进度

## 前置条件

1. **任务已规划**：go-sdk-planner 已创建 SUBTASKS.md
2. **子任务目录存在**：所有子任务目录已创建
3. **Hook 配置已加载**：.claude-plugin/hooks.json 已配置

## 工作流程

```
┌─────────────────┐
│  go-sdk-planner │  生成 SUBTASKS.md 和子任务目录
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  go-sdk-tracker │  更新 STATUS 文件
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  coordinator   │  监控 STATUS 变化，触发其他技能
└────────┬────────┘
         │ 检测到 completed
         ▼
┌─────────────────┐
│ /code-reviewer │  代码审查
└────────┬────────┘
         │ 审查通过
         ▼
┌─────────────────┐
│ /doc-verifier  │  文档验证
└────────┬────────┘
         │ 验证通过
         ▼
┌─────────────────┐
│  进入下一子任务 │
└─────────────────┘
```

## Hook 机制

### 配置文件：`.claude-plugin/hooks.json`

```json
{
  "hooks": {
    "on_task_in_progress": {
      "trigger": "when STATUS file contains 'in_progress'",
      "action": "log_progress",
      "description": "记录任务进度"
    },
    "on_task_completed": {
      "trigger": "when STATUS file changes to 'completed'",
      "action": "/code-reviewer",
      "args": "--task={{ .TaskID }}",
      "description": "自动触发代码审查"
    },
    "on_review_completed": {
      "trigger": "when REVIEW_COMMENTS.md exists and approved=true",
      "action": "/doc-verifier",
      "args": "--task={{ .TaskID }}",
      "description": "自动触发文档验证"
    },
    "on_all_subtasks_completed": {
      "trigger": "when all subtasks STATUS = 'completed'",
      "action": "generate_final_report",
      "description": "生成最终验收报告"
    }
  }
}
```

## 触发条件

### on_task_in_progress
- **触发时机**：STATUS 文件内容为 `in_progress`
- **执行动作**：记录日志，更新 SUBTASKS.md

### on_task_completed
- **触发时机**：STATUS 文件从其他状态变为 `completed`
- **执行动作**：
  1. 验证文件完整性
  2. 触发 `/code-reviewer` 技能
  3. 等待审查结果

### on_review_completed
- **触发时机**：REVIEW_COMMENTS.md 存在且标记为已批准
- **执行动作**：触发 `/doc-verifier` 技能

### on_doc_verified
- **触发时机**：DOC_VERIFICATION.md 存在且标记为通过
- **执行动作**：
  1. 更新子任务状态为 completed
  2. 检查是否有下一子任务
  3. 如果有，触发下一子任务

### on_all_subtasks_completed
- **触发时机**：所有子任务状态为 completed
- **执行动作**：
  1. 生成最终验收报告
  2. 清理临时文件
  3. 通知任务完成

## 状态管理

### 读取状态
```python
def read_task_status(task_path: Path) -> str:
    status_file = task_path / "STATUS"
    if not status_file.exists():
        return "pending"
    with open(status_file, 'r') as f:
        return f.read().strip()
```

### 检查是否所有子任务完成
```python
def all_subtasks_completed(subtasks_dir: Path) -> bool:
    for task_dir in subtasks_dir.glob("task-*"):
        status = read_task_status(task_dir)
        if status != "completed":
            return False
    return True
```

## 错误恢复

### 技能执行失败
当触发的技能执行失败时：

1. 记录错误日志
2. 设置子任务状态为 blocked
3. 生成错误报告
4. 通知用户手动干预

### 状态不一致
当检测到状态不一致时：

1. 验证 STATUS 文件内容
2. 检查文件完整性
3. 更新 SUBTASKS.md 以匹配实际状态
4. 记录不一致日志

## 进度反馈

### 控制台输出
```
[go-sdk-coordinator] 任务 1/4: 设计阶段 - in_progress
[go-sdk-coordinator] 任务 1/4: 设计阶段 - completed
[go-sdk-coordinator] 触发 /code-reviewer
[code-reviewer] 正在审查代码...
[code-reviewer] 审查完成，发现 3 个问题
[go-sdk-coordinator] 任务 1/4: 已阻塞（等待修复）
```

### 进度文件
生成 `COORDINATOR_PROGRESS.md`：
```markdown
# 协调进度

## 任务进度
- [x] task-01 - 设计阶段 - completed
- [ ] task-02 - 实现阶段 - in_progress
- [ ] task-03 - 测试阶段 - pending

## 当前状态
正在执行：task-02 实现阶段
等待：code-reviewer 审查结果
```

## 注意事项

### 技能依赖
- 依赖 go-sdk-tracker 维护 STATUS 文件
- 依赖 code-reviewer 和 doc-verifier 技能存在

### Hook 限制
- Hook 只能触发已注册的技能
- 技能间不能循环触发
- 必须有明确的完成条件

### 调试模式
启用调试模式可查看详细的 Hook 执行日志：
```bash
export COORDINATOR_DEBUG=true
```
