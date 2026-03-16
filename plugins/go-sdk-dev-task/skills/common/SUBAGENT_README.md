# Subagent 基础设施

这是华为云 OBS SDK Go 开发技能系统的 Subagent 基础设施模块，提供了完整的 Subagent 管理、消息传递和错误处理功能。

## 架构概述

### 核心组件

1. **SubagentManager** (`subagent_manager.py`)
   - Subagent 生命周期管理
   - 消息路由和传递
   - 状态同步和监控

2. **MessageProtocol** (`message_protocol.py`)
   - 消息数据结构定义
   - 消息队列实现
   - 消息路由器

3. **ErrorHandler** (`error_handler.py`)
   - Subagent 特定错误类型
   - 可恢复性检查
   - 重试机制

4. **Config** (`config.py`)
   - Subagent 配置管理
   - 技能级别配置
   - 环境变量支持

## 快速开始

### 1. 创建 Subagent Manager

```python
from common.subagent_manager import SubagentManager, SubagentManagerFactory
from common.config import Config

# 创建配置
config = Config()
config.set('subagent.enabled', True)

# 创建 Manager
manager = SubagentManagerFactory.create_manager(config)
manager.start()
```

### 2. 创建和启动 Subagent

```python
# 创建 subagent
agent_id = manager.create_subagent(
    skill_id="go-sdk-ut",
    task_id="write-unit-tests",
    metadata={
        'test_files': ['client_test.go', 'util_test.go']
    }
)

# 定义执行函数
def execute_unit_tests(context: dict) -> dict:
    # 执行测试逻辑
    return {
        'tests_run': 42,
        'tests_passed': 42,
        'coverage': 0.85
    }

# 启动 subagent
manager.start_subagent(agent_id, execute_unit_tests)
```

### 3. 等待结果

```python
# 等待单个 subagent
result = manager.wait_for_subagent(agent_id, timeout=30)
print(f"结果: {result}")

# 等待多个 subagents
results = manager.wait_for_all_subagents("go-sdk-ut", task_id, timeout=60)
print(f"所有结果: {results}")
```

### 4. 清理

```python
manager.stop()
```

## 并行执行示例

### 并行测试执行

```python
# 创建多个 subagents
agents = []

# 单元测试
agent_id1 = manager.create_subagent("go-sdk-ut", "test-task")
agents.append(agent_id1)

# 模糊测试
agent_id2 = manager.create_subagent("go-sdk-fuzz", "test-task")
agents.append(agent_id2)

# 性能测试
agent_id3 = manager.create_subagent("go-sdk-perf", "test-task")
agents.append(agent_id3)

# 并行启动
for agent_id in agents:
    manager.start_subagent(agent_id, execute_test_function)

# 等待所有完成
results = manager.wait_for_all_subagents("go-sdk-ut", "test-task")
```

## 消息传递

### 发送消息

```python
from common.message_protocol import SubagentMessage, MessageType, SubagentState

# 创建状态消息
message = SubagentMessage.create_status_message(
    skill_id="go-sdk-ut",
    task_id="write-unit-tests",
    status=SubagentState.RUNNING,
    progress=0.5,
    session_id=manager.session_id
)

# 发送消息
manager.send_message(message)
```

### 注册消息回调

```python
def on_status(message: SubagentMessage):
    print(f"状态更新: {message.payload}")

def on_result(message: SubagentMessage):
    print(f"执行结果: {message.payload}")

manager.register_message_callback(MessageType.STATUS, on_status)
manager.register_message_callback(MessageType.RESULT, on_result)
```

## 配置选项

### 全局配置

```yaml
subagent:
  enabled: true                # 是否启用 subagent
  parallel_workers: 2           # 并行工作数
  research_timeout: 300.0       # 研究超时（秒）
  execution_timeout: 600.0       # 执行超时（秒）
  heartbeat_interval: 30.0       # 心跳间隔（秒）
  max_retries: 3                # 最大重试次数
  retry_delay: 2.0              # 重试延迟（秒）
  message_queue_size: 100       # 消息队列大小
```

### 技能级别配置

```yaml
subagent:
  skills:
    go-sdk-ut:
      enabled: true
      parallel_workers: 4
      timeout: 300.0

    code-reviewer:
      enabled: true
      parallel_workers: 2
      timeout: 600.0
```

## 错误处理

### Subagent 错误类型

```python
from common.error_handler import (
    SubagentError,
    SubagentTimeoutError,
    SubagentExecutionError,
    SubagentCommunicationError
)

# 检查错误是否可恢复
error = manager.get_subagent_error(agent_id)
if error and error.is_recoverable():
    # 可以重试
    pass
```

### 重试机制

```python
# 使用配置的重试机制
config.set('subagent.max_retries', 3)
config.set('subagent.retry_delay', 2.0)

# 或者手动重试
try:
    result = manager.wait_for_subagent(agent_id, timeout=30)
except SubagentTimeoutError as e:
    if e.is_recoverable():
        # 重试逻辑
        manager.start_subagent(agent_id, execute_function)
```

## 与现有技能集成

### 在 Skill 中使用

```python
from common.skill_base import SkillBase
from common.subagent_manager import SubagentManagerFactory

class MySkill(SkillBase):
    def execute(self, context: dict) -> dict:
        # 检查是否启用 subagent
        if self.config.is_subagent_enabled():
            # 创建 manager
            manager = SubagentManagerFactory.create_for_skill(self)
            manager.start()

            try:
                # 使用 subagent 执行任务
                # ...
                pass
            finally:
                manager.stop()
        else:
            # 原有逻辑
            pass
```

## 状态查询

### Subagent 状态

```python
# 获取单个 subagent 信息
info = manager.get_subagent_info(agent_id)
print(f"状态: {info.state.value}")
print(f"进度: {info.progress}")

# 获取任务状态
status = manager.get_task_status("go-sdk-ut", "write-unit-tests")
print(f"整体状态: {status['overall_state']}")
print(f"已完成: {status['completed']}/{status['total_agents']}")
```

## 示例代码

完整的示例代码可以在 `subagent_examples.py` 中找到：

```bash
# 基本使用
python subagent_examples.py basic

# 并行执行
python subagent_examples.py parallel

# 消息回调
python subagent_examples.py callbacks

# 错误处理
python subagent_examples.py error

# 技能集成
python subagent_examples.py integration
```

## API 参考

### SubagentManager

| 方法 | 描述 |
|------|------|
| `start()` | 启动 Manager |
| `stop()` | 停止 Manager |
| `create_subagent()` | 创建新的 Subagent |
| `start_subagent()` | 启动 Subagent |
| `stop_subagent()` | 停止 Subagent |
| `wait_for_subagent()` | 等待 Subagent 完成 |
| `wait_for_all_subagents()` | 等待所有 Subagents 完成 |
| `get_subagent_info()` | 获取 Subagent 信息 |
| `get_subagent_state()` | 获取 Subagent 状态 |
| `get_subagent_result()` | 获取 Subagent 结果 |
| `get_task_status()` | 获取任务状态 |
| `send_message()` | 发送消息 |
| `register_message_callback()` | 注册消息回调 |

### SubagentMessage

| 静态方法 | 描述 |
|---------|------|
| `create_status_message()` | 创建状态消息 |
| `create_result_message()` | 创建结果消息 |
| `create_request_message()` | 创建请求消息 |
| `create_error_message()` | 创建错误消息 |
| `create_heartbeat_message()` | 创建心跳消息 |

## 最佳实践

1. **资源管理**
   - 始终调用 `manager.stop()` 清理资源
   - 使用 try-finally 确保资源释放

2. **错误处理**
   - 检查错误的可恢复性
   - 合理设置超时时间
   - 使用重试机制提高成功率

3. **并发控制**
   - 根据系统资源设置合理的并行工作数
   - 避免创建过多的 subagents

4. **状态监控**
   - 定期查询任务状态
   - 使用消息回调实时更新

5. **配置管理**
   - 使用环境变量覆盖配置
   - 为不同技能设置不同的超时时间

## 性能考虑

- **内存使用**: 每个 Subagent 消息队列默认大小为 100
- **并发性能**: 建议并行工作数不超过 CPU 核心数的 2 倍
- **网络通信**: 消息传递使用内存队列，性能开销较小
- **状态同步**: 状态更新使用线程锁，保证数据一致性

## 故障恢复

- **崩溃恢复**: Manager 重启后需要重新创建 Subagents
- **消息丢失**: 重启后消息队列会被清空
- **状态持久化**: 当前状态保存在内存中，重启后丢失

## 扩展开发

### 自定义消息类型

```python
class CustomMessageType(Enum):
    CUSTOM = "custom"

class CustomSubagentMessage(SubagentMessage):
    # 自定义消息类型
    pass
```

### 自定义错误类型

```python
from common.error_handler import SubagentError

class MyCustomError(SubagentError):
    def __init__(self, message: str, subagent_id: str = None):
        super().__init__(
            message,
            subagent_id=subagent_id,
            code=7000,  # 自定义错误码
            suggestion="自定义建议"
        )

    def is_recoverable(self) -> bool:
        # 自定义恢复逻辑
        return False
```

## 支持和反馈

如有问题或建议，请联系华为云 OBS SDK Team。
