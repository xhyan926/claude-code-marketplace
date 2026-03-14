# Google Go Style Guide 规范映射表

## 概述

本文档基于 Google Go Style Guide 和 Uber Go Guide，为华为云 OBS SDK 开发工具制定统一的 Go 编码规范映射。

## 命名规范映射

### 1. 包命名 (Package Names)

| Google 规范 | Uber 规范 | 当前实现 | 建议 |
|-------------|-----------|----------|------|
| 小写、简洁、描述性 | 小写、避免缩写 | 检查当前包名 | 统一为小写，避免缩写 |
| 不复用标准库名 | - | - | 避免使用标准库名称 |
| 单词用下划线分隔 | 单词用下划线分隔 | 部分符合 | 确保全部符合 |

**示例**：
```go
// 推荐
package obsclient
package xmlutils
package auth

// 避免
package obsSDK  // SDK 是缩写
package obs     // 过于简单
package http    // 与标准库冲突
```

### 2. 函数命名 (Function Names)

| Google 规范 | Uber 规范 | 当前实现 | 建议 |
|-------------|-----------|----------|------|
| 首字母大写（Public） | 首字母大写（Public） | 基本符合 | 保持当前规范 |
| 首字母小写（Private） | 首字母小写（Private） | 基本符合 | 保持当前规范 |
| 简洁、描述性强 | 简洁、描述性强 | 需要改进 | 增强描述性 |
| 避免过度缩写 | 避免过度缩写 | 需要改进 | 减少缩写使用 |

**示例**：
```go
// 推荐
func GetStringToInt64(input string, defaultValue int64) (int64, error)
func CreateObsClient(config *Config) (*Client, error)
func ValidateBucketName(name string) bool

// 避免
func StrToInt64(s string, d int64) (int64, error)  // 缩写过多
func ClientCreate(c *Config) (*Client, error)      // 顺序混乱
func ValidateBucket(b string) bool                  // 缩写
```

### 3. 变量命名 (Variable Names)

| Google 规范 | Uber 规范 | 当前实现 | 建议 |
|-------------|-----------|----------|------|
| 首字母小写（Private） | 首字母小写（Private） | 基本符合 | 保持当前规范 |
| 短变量名用于循环 | 短变量名用于循环 | 符合 | 继续使用 |
| 慎用单字符变量 | 慎用单字符变量 | 需要改进 | 减少单字符使用 |
| 避免过度缩写 | 避免过度缩写 | 需要改进 | 增强可读性 |

**示例**：
```go
// 推荐
func processFiles(files []string) error {
    for _, file := range files {
        content, err := readFile(file)
        if err != nil {
            return fmt.Errorf("failed to read %s: %w", file, err)
        }
        // ...
    }
}

// 避免
func processFiles(fs []string) error {
    for _, f := range fs {
        c, err := readFile(f)
        if err != nil {
            return err  // 缺少上下文
        }
        // ...
    }
}
```

### 4. 常量命名 (Constants)

| Google 规范 | Uber 规范 | 当前实现 | 建议 |
|-------------|-----------|----------|------|
| 首字母大写 | 首字母大写 | 基本符合 | 保持当前规范 |
| 帕斯卡命名法 | 帕斯卡命名法 | 符合 | 继续使用 |
| 避免无意义的命名 | 避免无意义的命名 | 需要改进 | 增强描述性 |

**示例**：
```go
// 推荐
const MaxRetries = 3
const ObsEndpoint = "https://obs.cn-north-4.myhuaweicloud.com"
const DefaultTimeout = 30 * time.Second

// 避免
const max = 3  // 无描述性
const end = "https://obs.cn-north-4.myhuaweicloud.com"  // 过于简单
```

## 文档注释规范映射

### 1. 函数文档注释

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 每个导出函数都需要注释 | 部分缺失 | 强制要求注释 |
| 参数说明、返回值说明、错误说明 | 格式不统一 | 标准化格式 |
| 包含使用示例 | 部分包含 | 添加完整示例 |

**标准格式**：
```go
// GetStringToInt64 将字符串转换为 int64
//
// 参数:
//   input: 要转换的字符串
//   defaultValue: 转换失败时的默认值
//
// 返回值:
//   int64: 转换后的整数，或默认值
//   error: 转换错误
func GetStringToInt64(input string, defaultValue int64) (int64, error) {
    // 实现
}
```

### 2. 类型文档注释

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 导出类型需要注释 | 部分缺失 | 强制要求注释 |
| 说明类型的用途和不变量 | 简单描述 | 增强详细说明 |
| 包含重要的使用限制 | 缺少限制 | 添加限制说明 |

## 错误处理规范映射

### 1. 错误返回

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 使用 error 作为最后一个返回值 | 基本符合 | 保持当前规范 |
| 错误信息清晰描述问题 | 部分模糊 | 增强描述性 |
| 使用 %w 包装错误 | 部分使用 | 统一使用 %w |

**最佳实践**：
```go
// 推荐
func ProcessData(data []byte) (*Result, error) {
    if len(data) == 0 {
        return nil, fmt.Errorf("empty data input")
    }

    parsed, err := parseJSON(data)
    if err != nil {
        return nil, fmt.Errorf("failed to parse JSON: %w", err)
    }

    return validate(parsed)
}

// 避免
func ProcessData(data []byte) (*Result, error) {
    if len(data) == 0 {
        return nil, errors.New("error")
    }

    parsed, err := parseJSON(data)
    if err != nil {
        return nil, err  // 缺少上下文
    }

    return parsed, nil
}
```

### 2. 错误检查

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 使用 errors.Is 检查错误类型 | 部分使用 | 统一使用 |
| 使用 errors.As 检查具体错误类型 | 部分使用 | 统一使用 |
| 避免字符串比较错误类型 | 有使用实例 | 完全避免 |

**最佳实践**：
```go
// 推荐
func handleRequest(ctx context.Context, req *Request) error {
    err := processRequest(ctx, req)
    if errors.Is(err, context.DeadlineExceeded) {
        return fmt.Errorf("request timed out: %w", err)
    }
    if errors.Is(err, ErrInvalidRequest) {
        return fmt.Errorf("invalid request: %w", err)
    }
    return err
}

// 避免
func handleRequest(ctx context.Context, req *Request) error {
    err := processRequest(ctx, req)
    if err.Error() == "context deadline exceeded" {  // 字符串比较
        return fmt.Errorf("request timed out: %w", err)
    }
    return err
}
```

## 代码结构规范映射

### 1. 包结构

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 包级别变量使用 var | 使用 var | 保持当前规范 |
| 简短的初始化函数 | 有实现 | 继续使用 |
| main 包特殊处理 | - | 需要考虑 |

### 2. 函数长度

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 避免过长的函数 | 部分过长 | 需要拆分 |
| 20-50 行为佳 | 不稳定 | 建议目标 |
| 最多 100 行 | 有超过 100 的 | 严格限制 |

### 3. 嵌套层级

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 避免深层嵌套 | 部分嵌套深 | 需要减少 |
| 最多 4 层嵌套 | 有超过的 | 严格限制 |
| 提前返回减少嵌套 | 有使用 | 继续使用 |

## 测试规范映射

### 1. 测试文件命名

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| `_test.go` 后缀 | 使用 _test.go | 保持当前规范 |
| 内部测试使用 `_internal_test.go` | 使用 _internal_test.go | 保持当前规范 |
| 测试文件与源文件同目录 | 符合 | 保持当前规范 |

### 2. 测试函数命名

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 首字母大写 | 使用首字母大写 | 保持当前规范 |
| 描述性强 | 当前 BDD 风格 | 简化为更简洁格式 |
| TestXxx 格式 | 符合 | 保持当前规范 |

**简化后的命名**：
```go
// 当前（BDD 风格）
TestStringToInt64_ShouldReturnDefaultValue_WhenValueIsEmptyString

// 简化后（Google 推荐）
TestStringToInt64_EmptyString_ReturnsDefault
```

### 3. 测试结构

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 表格驱动测试 | 使用表格测试 | 保持当前规范 |
| 边界条件测试 | 部分缺少 | 增加边界测试 |
| 错误情况测试 | 基本覆盖 | 继续覆盖 |

## LSP 集成规范

### 1. 类型定义

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 明确的类型定义 | 有明确类型 | 保持当前规范 |
| 避免接口过度设计 | 部分过度设计 | 优化接口 |
| 使用具体类型而非 interface{} | 部分使用 | 减少使用 |

### 2. 导入管理

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 标准库导入优先 | 部分混乱 | 标准化导入顺序 |
| 第三方库导入次之 | 符合 | 保持当前规范 |
| 本地包导入最后 | 符合 | 保持当前规范 |

**导入顺序**：
```go
import (
    // 标准库
    "context"
    "fmt"
    "net/http"

    // 第三方库
    "github.com/stretchr/testify/assert"
    "golang.org/x/oauth2"

    // 本地包
    "github.com/huawei-cloud-obs/obs-sdk-go"
    "github.com/huawei-cloud-obs/obs-sdk-go/auth"
)
```

### 3. 代码格式化

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| gofmt 自动格式化 | 使用 gofmt | 保持当前规范 |
| 行长度 80-100 字符 | 部分超长 | 限制行长度 |
| 避免长函数调用 | 部分过长 | 拆分长调用 |

## 特殊场景处理

### 1. 并发编程

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 使用 context 管理超时 | 部分使用 | 统一使用 |
| 避免全局变量 | 避免全局 | 保持当前规范 |
| 使用 sync 包 | 使用 sync | 保持当前规范 |

### 2. 错误传播

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 使用 fmt.Errorf 包装 | 部分使用 | 统一使用 |
| 保持错误栈信息 | 使用 %w | 保持当前规范 |
| 避免重复错误检查 | 部分重复 | 优化错误处理 |

### 3. 资源管理

| Google 规范 | 当前实现 | 建议 |
|-------------|----------|------|
| 使用 defer 释放资源 | 使用 defer | 保持当前规范 |
| 使用 defer.Close() | 使用 Close() | 保持当前规范 |
| 及时释放不必要资源 | 部分延迟 | 优化资源释放 |

## 实施检查清单

### 实施前检查

- [ ] 确认当前代码库的命名规范现状
- [ ] 识别需要改进的代码模式
- [ ] 制定迁移策略
- [ ] 准备自动化检查工具

### 实施中检查

- [ ] 命名规范是否符合 Google 标准
- [ ] 文档注释是否完整清晰
- [ ] 错误处理是否规范
- [ ] LSP 友好性是否达标

### 实施后检查

- [ ] 所有代码通过 go vet
- [ ] 所有代码通过 gofmt
- [ ] LSP 类型检查通过
- [ ] 文档覆盖率达标

## 迁移指南

### 1. 渐进式迁移

1. 第一阶段：新建代码使用新规范
2. 第二阶段：重构现有关键代码
3. 第三阶段：批量重构剩余代码

### 2. 自动化工具

- 使用 gofmt 格式化代码
- 使用 go vet 检查错误
- 使用 golangci-lint 进行静态分析
- 使用 LSP 实时检查

### 3. 测试验证

- 单元测试覆盖核心功能
- 集成测试验证兼容性
- 性能测试确保性能不受影响
- 用户测试收集反馈