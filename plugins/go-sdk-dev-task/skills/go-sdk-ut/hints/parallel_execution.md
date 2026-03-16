---
title: 单元测试并行执行
description: 使用 Subagent Manager 实现单元测试的并行执行，提升测试效率
---

# 单元测试并行执行提示词

## 概述

本提示词指导如何使用 Subagent Manager 实现单元测试的并行执行，显著提升测试效率。通过将测试任务分解为多个独立的子任务，可以同时运行多个测试套件。

## 启用条件

当满足以下条件时，启用单元测试的并行执行：

1. 用户明确要求快速执行测试
2. 测试文件数量超过 5 个
3. 配置中启用了 `subagent.enabled`
4. 项目有足够的计算资源

## 实施步骤

### 1. 任务分解

分析测试文件列表，将测试任务分解为独立的子任务：

```python
# 任务分解示例
test_tasks = [
    {
        'skill_id': 'go-sdk-ut',
        'task_id': 'unit-test-1',
        'metadata': {
            'test_file': 'client_test.go',
            'target_coverage': 0.8
        },
        'execute_func': execute_unit_test
    },
    {
        'skill_id': 'go-sdk-ut',
        'task_id': 'unit-test-2',
        'metadata': {
            'test_file': 'util_test.go',
            'target_coverage': 0.8
        },
        'execute_func': execute_unit_test
    }
]
```

### 2. 创建 Subagent Manager

使用 `SubagentManagerFactory` 创建 Manager：

```python
from skills.common import SubagentManagerFactory, Config

config = Config()
config.set('subagent.enabled', True)
config.set('subagent.parallel_workers', 4)

manager = SubagentManagerFactory.create_manager(config)
manager.start()
```

### 3. 并行启动测试

为每个测试任务创建并启动 Subagent：

```python
agent_ids = []
for task in test_tasks:
    # 创建 Subagent
    agent_id = manager.create_subagent(
        skill_id=task['skill_id'],
        task_id=task['task_id'],
        metadata=task['metadata']
    )

    # 启动 Subagent
    manager.start_subagent(agent_id, task['execute_func'])
    agent_ids.append(agent_id)
```

### 4. 等待所有测试完成

使用 `wait_for_all_subagents` 等待所有子任务完成：

```python
results = manager.wait_for_all_subagents(
    skill_id="go-sdk-ut",
    task_id="unit-test-1",
    timeout=600.0
)

# 处理结果
for agent_id, result in results.items():
    if result:
        print(f"测试 {agent_id} 成功: {result}")
    else:
        error = manager.get_subagent_error(agent_id)
        print(f"测试 {agent_id} 失败: {error}")
```

### 5. 生成聚合报告

汇总所有子任务的结果，生成统一的测试报告：

```json
{
  "total_tests": 150,
  "passed": 145,
  "failed": 5,
  "skipped": 0,
  "coverage": 82.5,
  "execution_time": "45s",
  "subtasks": [
    {
      "name": "subtask-1",
      "tests": 50,
      "passed": 48,
      "failed": 2,
      "coverage": 80.0
    }
  ]
}
```

## 进度报告

并行执行期间，定期报告进度：

```
[Subagent] go-sdk-ut:subtask-1 进度: 50% (测试文件: 5/10)
[Subagent] go-sdk-ut:subtask-2 进度: 30% (测试文件: 3/10)
[Subagent] go-sdk-ut:subtask-3 进度: 80% (测试文件: 8/10)
[Subagent] 所有子任务完成
```

## 性能优化建议

### 1. 合理设置并行工作数

- 单核机器：建议 1-2 个 workers
- 双核机器：建议 2-3 个 workers
- 四核机器：建议 4-6 个 workers
- 八核机器：建议 6-8 个 workers

### 2. 任务独立性

确保每个子任务之间没有依赖关系：
- 每个子任务处理不同的测试文件
- 子任务之间不共享状态
- 独立的测试数据

### 3. 资源监控

实时监控资源使用：
- CPU 使用率不应超过 90%
- 内存使用应有合理上限
- 注意磁盘 I/O 瓶颈

## 错误处理

### 1. 子任务失败

当某个子任务失败时：
- 记录详细的错误信息
- 其他子任务继续执行
- 最终报告包含失败信息

### 2. 超时处理

设置合理的超时时间：
- 单元测试：默认 600 秒
- 可根据测试数量调整
- 支持配置自定义

### 3. 重试机制

对于可恢复的错误：
- 自动重试失败的子任务
- 最多重试 3 次
- 使用指数退避策略

## 最佳实践

1. **测试分组**：将相关测试文件分组到同一个子任务
2. **负载均衡**：确保每个子任务的测试数量相近
3. **资源隔离**：每个子任务使用独立的测试环境
4. **结果验证**：确保并行结果与串行结果一致
5. **日志记录**：详细记录每个子任务的执行过程

## 示例命令

```bash
# 启用并行执行
/go-sdk-ut --parallel

# 指定并行工作数
/go-sdk-ut --parallel --workers=4

# 执行特定测试文件
/go-sdk-ut --files=client_test.go,util_test.go --parallel

# 设置目标覆盖率
/go-sdk-ut --coverage=0.85 --parallel
```

## 注意事项

1. **依赖管理**：确保测试依赖已安装
2. **环境变量**：检查必要的环境变量
3. **并发安全**：确保测试代码并发安全
4. **资源清理**：每个子任务完成后清理资源
5. **结果一致性**：验证并行结果的正确性
