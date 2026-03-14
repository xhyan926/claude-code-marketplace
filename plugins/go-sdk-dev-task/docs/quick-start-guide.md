# Go 编码技能规范改进 - 快速开始指南

## 概述

本指南帮助你快速开始使用改进后的 Go 编码技能，包括 Google Go 规范、LSP 支持和质量验证。

## 核心改进

### 1. Google Go 规范集成

#### 命名规范
```python
from skills.common.naming_standards import GoNamingStandards

# 创建命名规范验证器
standards = GoNamingStandards()

# 验证包名
is_valid, errors = standards.validate_package_name("obsclient")
if not is_valid:
    print(f"包名无效: {errors}")

# 验证函数名
is_valid, errors = standards.validate_function_name("GetStringToInt64")
if not is_valid:
    print(f"函数名无效: {errors}")
```

#### 文档注释生成
```python
from skills.common.skill_base import SkillBase

# 创建技能实例
skill = YourSkill()

# 生成 Google 标准文档注释
params = [
    {"name": "input", "description": "输入字符串"},
    {"name": "defaultValue", "description": "默认值"}
]
returns = [
    {"type": "int64", "description": "转换后的整数"},
    {"type": "error", "description": "转换错误"}
]

doc_comment = skill.generate_go_doc_comment(
    "GetStringToInt64 将字符串转换为 int64",
    params,
    returns
)
print(doc_comment)
```

### 2. LSP 支持集成

#### LSP 验证
```python
from skills.common.lsp_support import LSPSupport

# 创建 LSP 支持
lsp = LSPSupport("/path/to/project")

# 验证代码 LSP 友好性
code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
"""

is_valid, errors = lsp.validate_lsp_friendly_code(code)
if not is_valid:
    print(f"代码不符合 LSP 规范: {errors}")
```

#### LSP 配置生成
```python
from skills.common.lsp_config import LSPConfigGenerator

# 创建配置生成器
generator = LSPConfigGenerator("/path/to/project")

# 生成所有配置
config_files = generator.generate_all_configs()
print("生成的配置文件:")
for name, path in config_files.items():
    print(f"  {name}: {path}")
```

### 3. 质量验证集成

#### 综合代码验证
```python
from skills.common.validators import Validator

# 初始化验证器
Validator.initialize_go_standards("/path/to/project")

# 综合验证代码
code = """
package main

func GetStringToInt64(input string, defaultValue int64) (int64, error) {
    return defaultValue, nil
}
"""

errors = Validator.validate_go_code_comprehensive(
    code,
    validate_lsp=True,
    validate_docs=True,
    validate_errors=True
)

if errors:
    print("验证发现问题:")
    for error in errors:
        print(f"  - {error}")
else:
    print("代码验证通过！")
```

## 使用改进后的技能

### 单元测试技能 (go-sdk-ut)

#### 生成 BDD 风格测试
```bash
/go-sdk-ut
```

**改进内容**:
- ✅ 保留 BDD 命名规范
- ✅ 添加 Google Go 文档注释
- ✅ 使用 t.Cleanup() 资源管理
- ✅ 改进的表格驱动测试
- ✅ 边界条件测试

### 模糊测试技能 (go-sdk-fuzz)

#### 生成标准化模糊测试
```bash
/go-sdk-fuzz
```

**改进内容**:
- ✅ 集成 Context 超时控制
- ✅ 崩溃处理增强
- ✅ 边界条件测试
- ✅ 性能监控
- ✅ Google Go 文档注释

### 性能测试技能 (go-sdk-perf)

#### 生成基准测试
```bash
/go-sdk-perf
```

**改进内容**:
- ✅ 多类型性能测试（轻量、深度、并发）
- ✅ 内存性能监控
- ✅ 资源使用监控
- ✅ 性能回归检测
- ✅ 可扩展性测试
- ✅ 详细的性能报告

### 集成测试技能 (go-sdk-integration)

#### 生成端到端测试
```bash
/go-sdk-integration
```

**改进内容**:
- ✅ 真实环境和 Mock 服务器测试
- ✅ 并发集成测试
- ✅ 超时和重试机制
- ✅ 大数据处理
- ✅ Context 集成
- ✅ 资源清理保证
- ✅ 错误处理测试

## LSP 配置使用

### VSCode 配置

生成的配置文件会自动配置 VSCode 以获得最佳 LSP 体验：

```json
{
  "go.useLanguageServer": true,
  "go.lintTool": "golangci-lint",
  "gopls": {
    "ui.diagnostic.staticcheck": true,
    "ui.completion.matcher": "fuzzy",
    "formatting.gofumpt": true
  }
}
```

### Go 环境变量

配置 Go 开发环境变量：

```bash
# 从生成的 .env.go 文件加载
source .env.go

# 手动设置（示例）
export GOPATH=/path/to/project
export GOPROXY=https://goproxy.cn,direct
export GO111MODULE=on
```

## 质量检查

### 自动化验证

#### 使用验证器
```python
from skills.common.validators import Validator

# 验证整个项目
errors = Validator.validate_go_file_comprehensive(
    Path("main.go"),
    validate_lsp=True,
    validate_docs=True,
    validate_errors=True
)
```

#### 运行 Go 标准工具
```bash
# 格式化代码
gofmt -w .

# 静态分析
go vet ./...

# 代码检查
golangci-lint run

# 测试覆盖率
go test -cover
```

### 质量标准

#### Google Go 规范检查点
- ✅ 包名小写、简洁
- ✅ 函数命名符合规范
- ✅ 文档注释完整
- ✅ 错误处理使用 %w
- ✅ 错误检查使用 errors.Is/As
- ✅ 导入语句规范（标准库优先）
- ✅ 代码通过 go vet
- ✅ 代码通过 gofmt

#### BDD 测试命名检查点
- ✅ 保留 Should_ExpectedResult_When_Condition_Given_State 格式
- ✅ 测试函数独立运行
- ✅ 使用 t.Cleanup() 清理资源
- ✅ 边界条件测试完整

## 故障排除

### 常见问题

#### Q1: LSP 配置不生效
**A**: 确保在 VSCode 中重新加载工作区：
1. 按 Cmd+Shift+P (Mac) 或 Ctrl+Shift+P (Windows/Linux)
2. 输入 "Reload Window"
3. 重新打开项目

#### Q2: 命名验证失败
**A**: 检查命名是否符合 Google Go 规范：
- 包名必须小写
- 公共函数名首字母大写
- 私有函数名首字母小写
- 避免使用缩写

#### Q3: 文档注释不符合要求
**A**: 确保文档注释符合 godoc 标准：
- 第一行是简短描述
- 参数使用 "// 参数:" 格式
- 返回值使用 "// 返回值:" 格式
- 包含使用示例

#### Q4: 错误处理验证失败
**A**: 检查错误处理是否规范：
- 使用 fmt.Errorf("context: %w", err) 包装错误
- 使用 errors.Is(err, target) 检查错误类型
- 避免字符串比较错误类型

## 下一步

### 1. 探索新功能
- 尝试不同的测试模板
- 使用 LSP 配置生成
- 探索质量验证功能

### 2. 定制配置
- 根据项目需求调整 LSP 配置
- 自定义验证规则
- 配置项目特定的设置

### 3. 集成到工作流
- 添加到 CI/CD 流程
- 集成到开发环境
- 建立代码审查标准

## 支持

### 文档资源
- `docs/google-go-style-guide-mapping.md` - Google Go 规范映射
- `docs/adjusted-implementation-plan.md` - 调整后的实施计划
- `docs/progress-summary.md` - 进度总结
- `docs/project-completion-summary.md` - 项目完成总结

### 源代码
- `skills/common/lsp_support.py` - LSP 支持模块
- `skills/common/naming_standards.py` - 命名规范模块
- `skills/common/lsp_config.py` - LSP 配置生成器
- `skills/common/validators.py` - 更新的验证器

### 获取帮助
如果遇到问题，请：
1. 检查相关文档
2. 查看示例代码
3. 提交 issue 或反馈

---

**开始使用改进后的 Go 编码技能，享受更好的代码质量和开发体验！**