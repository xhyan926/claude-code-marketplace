# 测试计划：{{ TASK_ID }} - {{ TASK_NAME }}

## 测试目标
{{ 描述测试要达到的目标 }}

## 测试范围

### 单元测试
- {{ 测试范围 1 }}
- {{ 测试范围 2 }}

### 集成测试
- {{ 测试范围 1 }}
- {{ 测试范围 2 }}

## 测试用例设计

### 单元测试用例
使用 BDD 命名规范：Should_ExpectedResult_When_Condition_Given_State

#### 正常场景
1. **Should_return_success_When_valid_input_Given_proper_parameters**
   - 输入：{{ 描述 }}
   - 预期：{{ 描述 }}
   - 验证点：{{ 列出 }}

2. **Should_return_correct_data_When_request_succeeds_Given_existing_resource**
   - 输入：{{ 描述 }}
   - 预期：{{ 描述 }}
   - 验证点：{{ 列出 }}

#### 异常场景
1. **Should_return_error_When_invalid_input_Given_empty_parameters**
   - 输入：{{ 描述 }}
   - 预期：{{ 描述 }}
   - 验证点：{{ 列出 }}

2. **Should_handle_timeout_When_network_slow_Given_long_running_operation**
   - 输入：{{ 描述 }}
   - 预期：{{ 描述 }}
   - 验证点：{{ 列出 }}

#### 边界场景
1. **Should_handle_large_data_When_file_size_is_5GB_Given_upload_operation**
   - 输入：{{ 描述 }}
   - 预期：{{ 描述 }}
   - 验证点：{{ 列出 }}

2. **Should_handle_concurrent_requests_When_multiple_clients_Given_high_load**
   - 输入：{{ 描述 }}
   - 预期：{{ 描述 }}
   - 验证点：{{ 列出 }}

### 集成测试用例
1. {{ 场景名称 }}
   - 步骤：{{ 描述 }}
   - 预期：{{ 描述 }}

2. {{ 场景名称 }}
   - 步骤：{{ 描述 }}
   - 预期：{{ 描述 }}

## 测试工具

### 必选工具
- **testify**：断言库
  ```go
  import "github.com/stretchr/testify/assert"
  import "github.com/stretchr/testify/suite"
  ```

- **httptest**：HTTP 服务器模拟
  ```go
  import "net/http/httptest"
  ```

- **gomonkey**：Mock 工具
  ```go
  import "github.com/agiledragon/gomonkey/v2"
  ```

### 可选工具
- {{ 其他测试工具 }}

## 测试策略

### Mock 策略
- **外部依赖**：使用 gomonkey mock
- **HTTP 请求**：使用 httptest 模拟服务器
- **文件操作**：使用临时文件

### 测试覆盖率
- **目标覆盖率**：≥80%
- **关键路径覆盖率**：≥90%
- **核心逻辑覆盖率**：100%

## 测试执行

### 测试命令
```bash
# 运行所有测试
go test ./... -v

# 运行特定包的测试
go test ./obs -v

# 运行特定测试函数
go test ./obs -run TestSpecificFunction -v

# 生成覆盖率报告
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out -o coverage.html
```

### 测试环境
- {{ 测试环境要求 }}

## 验收标准

### 功能验收
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码覆盖率达到目标

### 质量验收
- [ ] 测试用例符合 BDD 命名规范
- [ ] 测试代码清晰易读
- [ ] Mock 使用得当

### 文档验收
- [ ] 测试用例有完整注释
- [ ] 测试覆盖场景充分

## 与 go-sdk-ut skill 集成

### 测试编写阶段
**必须调用** `/go-sdk-ut` skill 进行测试编写：

```markdown
## 测试编写
使用 /go-sdk-ut skill 编写单元测试：
1. 确定测试场景
2. 按照 BDD 规范命名测试用例
3. 使用 testify 进行断言
4. 使用 httptest 模拟 HTTP 服务器
5. 使用 gomonkey 进行 mock
```

### 测试审查
- [ ] 是否遵循测试命名规范
- [ ] 测试用例是否充分
- [ ] Mock 使用是否正确
- [ ] 断言是否合理

## 风险和缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| {{ 风险描述 }} | {{ 影响等级 }} | {{ 具体措施 }} |

## 测试计划执行时间表

| 阶段 | 任务 | 预计时间 | 实际时间 |
|------|------|----------|----------|
| 单元测试编写 | {{ 任务 }} | {{ X 天 }} | {{ 天 }} |
| 集成测试编写 | {{ 任务 }} | {{ Y 天 }} | {{ 天 }} |
| 测试执行 | {{ 任务 }} | {{ Z 天 }} | {{ 天 }} |
| 测试修复 | {{ 任务 }} | {{ W 天 }} | {{ 天 }} |
