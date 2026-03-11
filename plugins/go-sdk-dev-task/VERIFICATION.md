# v2.0.0 验证清单

本文档用于验证 v2.0.0 的所有改进是否正确实现。

## 第一阶段：基础设施改进

### skills/common/ 目录结构
- [ ] `skills/common/__init__.py` 存在
- [ ] `skills/common/skill_base.py` 存在
- [ ] `skills/common/template_engine.py` 存在
- [ ] `skills/common/error_handler.py` 存在
- [ ] `skills/common/error_codes.json` 存在
- [ ] `skills/common/logger.py` 存在
- [ ] `skills/common/config.py` 存在
- [ ] `skills/common/validators.py` 存在
- [ ] `skills/common/retry.py` 存在

### 模板迁移
- [ ] 旧 `.md` 模板已删除
- [ ] 新 `.go.tmpl` 模板已创建
  - [ ] `subtask_template.go.tmpl`
  - [ ] `implementation_template.go.tmpl`
  - [ ] `test_plan_template.go.tmpl`
  - [ ] `acceptance_report_template.go.tmpl`
  - [ ] `acceptance_report_simple.go.tmpl`
  - [ ] `api_change_tracker.go.tmpl`
- [ ] 占位符语法已更新为 Go template

### 插件版本
- [ ] `plugin.json` 版本更新为 2.0.0

## 第二阶段：架构优化

### 共享模板库
- [ ] `templates/common/` 目录存在
- [ ] 测试基础设施模板存在
- [ ] 文档公共组件存在
- [ ] 代码片段库存在

### 新技能创建
#### go-sdk-planner
- [ ] `SKILL.md` 存在
- [ ] `evals/evals.json` 存在

#### go-sdk-tracker
- [ ] `SKILL.md` 存在
- [ ] `evals/evals.json` 存在
- [ ] `scripts/tracker.py` 存在
- [ ] `.claude-plugin/hooks.json` 存在

#### go-sdk-coordinator
- [ ] `SKILL.md` 存在
- [ ] `evals/evals.json` 存在
- [ ] `.claude-plugin/hooks.json` 存在

#### code-reviewer
- [ ] `SKILL.md` 存在
- [ ] `evals/evals.json` 存在
- [ ] `templates/review_comments_template.go.tmpl` 存在
- [ ] `.claude-plugin/hooks.json` 存在

#### doc-verifier
- [ ] `SKILL.md` 存在
- [ ] `evals/evals.json` 存在
- [ ] `templates/verification_report_template.go.tmpl` 存在
- [ ] `.claude-plugin/hooks.json` 存在

### 评估用例
- [ ] `go-sdk-ut/evals/evals.json` 存在
- [ ] `go-sdk-fuzz/evals/evals.json` 存在
- [ ] `go-sdk-perf/evals/evals.json` 存在
- [ ] `go-sdk-integration/evals/evals.json` 存在
- [ ] `sdk-doc/evals/evals.json` 存在

## 第三阶段：用户体验优化

### 命名规范统一
- [ ] `go-sdk-fuzz/SKILL.md` (原 skill.md)
- [ ] `go-sdk-perf/SKILL.md` (原 skill.md)
- [ ] `sdk-doc/SKILL.md` (原 skill.md)
- [ ] `go-sdk-integration/SKILL.md` (原 skill.md)

### 文档完善
- [ ] `CHANGELOG.md` 存在
- [ ] `CONTRIBUTING.md` 存在
- [ ] `README.md` 已更新
- [ ] `MIGRATION_GUIDE.md` 存在

### 用户体验功能
- [ ] `progress.py` 存在
- [ ] `interactive.py` 存在
- [ ] `triggers.py` 存在
- [ ] `context_detector.py` 存在

## 功能测试

### 技能导入
- [ ] `from skills.common import SkillBase` 可以导入
- [ ] `from skills.common import TemplateEngine` 可以导入
- [ ] `from skills.common import ErrorHandler` 可以导入

### 模板渲染
- [ ] Go template 语法可以正常工作
- [ ] 占位符 `{{ .VariableName }}` 可以正常替换
- [ ] 条件渲染 `{{ if }}...{{ end }}` 可以正常工作

### Hook 配置
- [ ] `.claude-plugin/hooks.json` 格式正确
- [ ] Hook 触发条件定义正确

## 快速功能测试

### 测试 1：模板渲染
```bash
cd /Users/xhyan/xhyan-plugins-market/plugins/go-sdk-dev-task/skills/common
python3 -c "from template_engine import TemplateEngine; engine = TemplateEngine(); print(engine.render_string('Hello {{ .Name }}!', {'Name': 'World'}))"
```
预期输出：`Hello World!`

### 测试 2：错误处理
```bash
cd /Users/xhyan/xhyan-plugins-market/plugins/go-sdk-dev-task/skills/common
python3 -c "from error_handler import ErrorHandler; h = ErrorHandler(); h.handle(Exception('Test error'))"
```
预期输出：友好的错误信息

### 测试 3：验证器
```bash
cd /Users/xhyan/xhyan-plugins-market/plugins/go-sdk-dev-task/skills/common
python3 -c "from validators import Validator; v = Validator(); v.validate_status('completed'); print('Validation passed')"
```
预期输出：`Validation passed`

## 统计验证

### 文件统计
```bash
find skills -name "*.py" | wc -l
```
预期：至少 10 个 Python 文件

### 模板统计
```bash
find skills -name "*.go.tmpl" | wc -l
```
预期：至少 10 个模板文件

### 评估用例统计
```bash
find skills -name "evals.json" | wc -l
```
预期：10 个评估文件

## 已知问题

记录验证过程中发现的任何问题：

1.
2.
3.

## 下一步行动

- [ ] 所有验证通过后，可以开始使用新的技能系统
- [ ] 如果有失败项目，需要修复后重新验证
- [ ] 记录用户反馈，用于后续改进
