# Common Framework

Go SDK 开发技能通用框架，提供以下核心功能：

## 模块说明

### skill_base.py
技能基类，定义统一的技能执行接口。所有技能应继承此类并实现 `execute()` 方法。

### template_engine.py
模板引擎，支持 Go template 语法（使用 jinja2 实现），包括：
- 条件渲染：`{{ if .Condition }}...{{ end }}`
- 循环：`{{ range .Items }}...{{ end }}`
- 模板包含：`{{ template "partial" . }}`
- 点表示法：`{{ .Nested.Variable }}`

### error_handler.py
错误处理模块，定义统一的错误码体系和错误处理机制。

### error_codes.json
错误码定义文件，包含所有技能的错误码。

### logger.py
日志记录模块，提供结构化日志记录功能。

### config.py
配置管理模块，支持 YAML 配置文件和环境变量覆盖。

### validators.py
验证器集合，提供常用的验证功能。

### retry.py
重试机制，支持指数退避策略。

### subagent_manager.py
Subagent 管理器，提供 Subagent 的生命周期管理、消息路由和状态同步功能。
用于实现并行执行和深度代码研究。

### message_protocol.py
消息传递协议，定义 Subagent 之间的消息数据结构和通信机制。

### subagent_examples.py
Subagent 使用示例代码，展示各种常见使用场景。

### SUBAGENT_README.md
Subagent 基础设施的详细使用文档，包含 API 参考和最佳实践。

## 使用示例

### 创建新技能

```python
from skills.common import SkillBase, get_logger

class MySkill(SkillBase):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)

    def execute(self, context: dict) -> dict:
        self.logger.info("开始执行技能")
        # 实现技能逻辑
        return {"status": "success"}
```

### 使用模板引擎

```python
from skills.common import TemplateEngine

engine = TemplateEngine()
result = engine.render("template.go.tmpl", {"TaskID": "task-01", "TaskName": "设计阶段"})
```

### 使用错误处理

```python
from skills.common import ErrorHandler, SkillError

error_handler = ErrorHandler()
try:
    # 执行可能出错的代码
    pass
except SkillError as e:
    error_handler.handle(e)
```

### 使用 Subagent Manager

```python
from skills.common import SubagentManagerFactory
from skills.common.config import Config

# 创建配置
config = Config()
config.set('subagent.enabled', True)

# 创建 Manager
manager = SubagentManagerFactory.create_manager(config)
manager.start()

try:
    # 创建 subagent
    agent_id = manager.create_subagent(
        skill_id="go-sdk-ut",
        task_id="write-unit-tests"
    )

    # 启动 subagent
    def execute_test(context: dict) -> dict:
        return {'tests_passed': 42}

    manager.start_subagent(agent_id, execute_test)

    # 等待结果
    result = manager.wait_for_subagent(agent_id, timeout=30)
finally:
    manager.stop()
```

详细的使用文档请参考 [SUBAGENT_README.md](SUBAGENT_README.md)。

## 版本信息

- 版本：2.0.0
- 更新日期：2026-03-16
- 新增功能：
  - Subagent 管理器
  - 消息传递协议
  - 并行执行支持
  - 深度代码研究能力
