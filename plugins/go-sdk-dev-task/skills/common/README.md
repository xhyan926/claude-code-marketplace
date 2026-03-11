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

## 版本信息

- 版本：1.0.0
- 更新日期：2026-03-11
