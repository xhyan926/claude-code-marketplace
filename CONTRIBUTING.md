# 贡献指南

感谢您对 Go SDK 开发任务插件市场的关注和贡献！

## 如何贡献

### 报告问题

如果您发现 bug 或有功能建议：

1. 搜索现有 [Issues](https://github.com/xhyan926/claude-code-marketplace/issues) 确认问题未报告
2. 创建新 Issue，使用清晰的标题和详细的描述
3. 添加相关标签（bug、enhancement、documentation 等）

### 提交代码

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 创建 Pull Request

## 开发规范

### 代码风格

- Python 代码遵循 PEP 8 规范
- 使用有意义的变量和函数命名
- 添加适当的注释和文档字符串

### 技能开发

#### SKILL.md 规范

每个技能必须包含 `SKILL.md` 文件，格式如下：

```markdown
---
name: skill-name
description: 技能描述
---

# skill-name

## 技能用途
...

## 前置条件
...

## 输入格式
...

## 输出格式
...

## 注意事项
...
```

#### 模板规范

- 使用 Go template 语法（`.go.tmpl` 扩展）
- 占位符使用英文点表示法（`{{ .VariableName }}`）
- 复用共享模板库中的组件

#### 评估用例

每个技能必须包含 `evals/evals.json`，包含至少 3-5 个评估用例：

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "prompt": "测试提示",
      "expected_output": "预期输出",
      "assertions": [
        {
          "name": "断言名称",
          "type": "file_exists | file_content",
          "path": "文件路径",
          "pattern": "正则表达式"
        }
      ]
    }
  ]
}
```

### 测试

运行所有评估用例：

```bash
# 使用 skill-creator 运行评估
/skill-creator run-evals skills/skill-name/evals/evals.json
```

### 文档

- 更新相关技能的 `SKILL.md`
- 如果有破坏性变更，更新 `CHANGELOG.md`
- 添加必要的代码注释

## Pull Request 流程

1. 确保 PR 描述清晰，包含：
   - 变更的目的
   - 修复的问题或实现的功能
   - 相关 Issue 的引用

2. 确保 PR 通过所有检查：
   - 代码风格检查
   - 评估用例通过
   - 文档完整

3. 保持 PR 小而专注：
   - 一个 PR 应该解决一个主要问题
   - 避免大规模重构
   - 如果需要，可以提交多个 PR

## 技能类型

### 可贡献的技能类型

1. **测试相关**：新的测试类型、测试工具集成
2. **文档相关**：文档生成、格式转换、验证
3. **代码质量**：代码审查、静态分析、性能检测
4. **开发辅助**：代码生成、模板管理、依赖管理

### 技能命名规范

- 使用 `go-sdk-` 前缀（与 Go SDK 开发相关）
- 使用小写字母和连字符
- 名称应清晰描述技能用途

## 问题标签

- `bug`：bug 报告
- `enhancement`：功能改进
- `documentation`：文档相关
- `good first issue`：适合新手的问题
- `help wanted`：需要帮助
- `priority: high/medium/low`：优先级

## 行为准则

- 尊重所有贡献者
- 建设性地提供反馈
- 关注问题，不针对个人
- 接受不同的意见和方法

## 获取帮助

- 查看 [SKILL.md](./plugins/go-sdk-dev-task/skills/go-sdk-dev-task/SKILL.md) 了解技能使用
- 加入 [Discord/Slack 社区](#)（如适用）
- 查阅项目 [CLAUDE.md](./CLAUDE.md)

## 许可证

通过贡献代码，您同意您的贡献将根据项目的许可证进行授权。
