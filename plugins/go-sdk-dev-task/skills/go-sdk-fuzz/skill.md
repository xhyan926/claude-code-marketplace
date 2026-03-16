# go-sdk-fuzz

## 技能概述

OBS SDK Go模糊测试编写指南。本技能指导用户如何为华为云OBS SDK识别关键输入解析函数并编写高质量的模糊测试，用于发现潜在的漏洞和边界条件问题。

## 使用场景

- 识别关键的输入解析函数
- 编写模糊测试发现潜在bug
- 测试XML解析、URL解析、签名验证等敏感功能
- 验证输入处理的鲁棒性

## 核心功能

### 1. 关键函数识别

自动识别需要模糊测试的关键函数：
- **XML解析函数**：`TransToXml`、`XmlToTrans`
- **URL解析函数**：endpoint处理、URL构造函数
- **签名验证函数**：`authV2_test.go`中的签名相关函数
- **响应解析函数**：各种API响应的解析函数

### 2. Fuzzing配置

配置模糊测试参数：
- 测试时长（默认30s）
- 工作线程数量
- 最大输入大小限制
- 种子文件管理

### 3. 崩溃分析流程

提供系统性的崩溃分析方法：
- 崩溃日志分析
- 输入复现
- 根本原因定位
- 修复建议

### 4. Fuzzing最佳实践

指导如何编写有效的模糊测试：
- 超时设置
- 输入边界
- 资源限制
- 性能监控

## 目标函数清单

### XML解析相关
- `TransToXml` - 将结构体转换为XML
- `XmlToTrans` - 将XML解析为结构体
- 各种XML解析辅助函数

### URL解析相关
- `New`函数中的endpoint处理
- URL构造和解析函数
- 路径处理函数

### 签名验证相关
- `authV2.go`中的签名生成函数
- `authV4.go`中的签名验证函数
- `SignatureObs`相关函数

### 响应解析相关
- 错误响应解析函数
- 成功响应解析函数
- 自定义头部解析函数

## 使用方法

### 基本用法

```bash
/go-sdk-fuzz
```

### 带参数使用

```bash
/go-sdk-fuzz --targets=xml,url,auth
/go-sdk-fuzz --duration=60s
/go-sdk-fuzz --workers=4
/go-sdk-fuzz --seeds=./fuzz_seeds/
```

### 技能输出

1. **模糊测试文件**：
   ```
   obs/*_fuzz_test.go
   ```

2. **目标函数列表**：
   - 关键函数识别结果
   - 测试优先级排序

3. **配置指南**：
   - fuzzing配置建议
   - 超时和资源设置

4. **分析工具**：
   - 崩溃分析脚本
   - 输入生成器

## 输出示例

### 生成的模糊测试文件示例

```go
//go:build fuzz

package obs

import (
	"testing"
	"github.com/huaweicloud/huaweicloud-sdk-go-obs/obs"
)

// FuzzTransToXml 测试XML解析函数
func FuzzTransToXml(f *testing.F) {
	// 添加种子数据
	seeds := []struct {
		input interface{}
	}{
		{&obs.CreateBucketInput{Bucket: "test"}},
		{&obs.PutObjectInput{Bucket: "test", Key: "test"}},
		{&obs.GetObjectInput{Bucket: "test", Key: "test"}},
	}

	for _, seed := range seeds {
		f.Add(seed.input)
	}

	// Fuzzing测试
	f.Fuzz(func(t *testing.T, input interface{}) {
		// 防止测试超时
		if len(f.Fuzzing()) > 10000 {
			t.Skip("跳过长时间运行")
		}

		// 执行XML转换
		xmlBytes, err := TransToXml(input)
		if err != nil {
			// 记录XML解析错误
			t.Logf("XML转换失败: %v, input: %v", err, input)
			return
		}

		// 验证生成的XML
		if len(xmlBytes) == 0 {
			t.Error("生成的XML为空")
		}
	})
}

// FuzzUrlParsing 测试URL解析函数
func FuzzUrlParsing(f *testing.F) {
	// 添加种子数据
	seeds := []string{
		"https://obs.cn-north-4.myhuaweicloud.com",
		"http://localhost:8080",
		"https://example.com/bucket/object",
		"https://example.com/bucket/",
	}

	for _, seed := range seeds {
		f.Add(seed)
	}

	// Fuzzing测试
	f.Fuzz(func(t *testing.T, urlStr string) {
		// 防止URL过长
		if len(urlStr) > 2048 {
			t.Skip("URL过长，跳过")
		}

		// 执行URL解析
		_, err := parseObsUrl(urlStr)
		if err != nil {
			// 记录解析错误
			t.Logf("URL解析失败: %v, url: %s", err, urlStr)
			return
		}
	})
}

// FuzzAuthSignature 测试签名验证函数
func FuzzAuthSignature(f *testing.F) {
	// 添加种子数据
	seeds := []struct {
		accessKey string
		secretKey string
		method    string
		path      string
	}{
		{"test", "test", "GET", "/"},
		{"test", "test", "PUT", "/bucket/object"},
		{"test", "test", "POST", "/bucket/object?uploadId=test"},
	}

	for _, seed := range seeds {
		f.Add(seed.accessKey, seed.secretKey, seed.method, seed.path)
	}

	// Fuzzing测试
	f.Fuzz(func(t *testing.T, accessKey, secretKey, method, path string) {
		// 防止凭据过长
		if len(accessKey) > 100 || len(secretKey) > 100 {
			t.Skip("凭据过长，跳过")
		}

		// 执行签名计算
		signature := calculateSignatureV4(accessKey, secretKey, method, path)
		if signature == "" {
			t.Error("签名生成失败")
		}
	})
}
```

### 崩溃分析报告示例

```json
{
  "crash_reports": [
    {
      "function": "TransToXml",
      "input": " malicious XML input here",
      "error": "xml: syntax error",
      "stack_trace": "...",
      "recommendation": "Add XML validation before parsing"
    },
    {
      "function": "parseObsUrl",
      "input": "https://[invalid-url]",
      "error": "parse failed",
      "stack_trace": "...",
      "recommendation": "Add URL validation"
    }
  ],
  "total_executions": 100000,
  "crashes_found": 2,
  "timeout_issues": 0
}
```

## 运行模糊测试

### 基本运行

```bash
# 运行所有模糊测试
go test -tags fuzz ./obs -fuzz=.

# 运行特定函数的模糊测试
go test -tags fuzz ./obs -fuzz=FuzzTransToXml

# 设置测试时长
go test -tags fuzz ./obs -fuzz=. -fuzztime=60s
```

### 使用工作线程

```bash
# 使用多个工作线程（并行执行）
go test -tags fuzz ./obs -fuzz=. -parallel=4
```

### 使用种子文件

```bash
# 使用种子文件启动
go test -tags fuzz ./obs -fuzz=FuzzFunction -fuzzinput=./seeds/
```

## 最佳实践

### 1. 输入边界设置

```go
f.Fuzz(func(t *testing.T, input string) {
    // 防止输入过大
    if len(input) > 1024*1024 { // 1MB限制
        t.Skip("输入过大，跳过")
    }

    // 执行测试...
})
```

### 2. 超时控制

```go
f.Fuzz(func(t *testing.T, input interface{}) {
    // 防止测试运行时间过长
    if len(f.Fuzzing()) > 10000 {
        t.Skip("跳过长时间运行")
    }

    // 执行测试...
})
```

### 3. 资源监控

```go
f.Fuzz(func(t *testing.T, input interface{}) {
    // 检查内存使用
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    if m.Alloc > 100*1024*1024 { // 100MB限制
        t.Skip("内存使用过高，跳过")
    }

    // 执行测试...
})
```

### 4. 错误记录

```go
f.Fuzz(func(t *testing.T, input interface{}) {
    // 执行测试
    result, err := processInput(input)
    if err != nil {
        // 记录错误但不崩溃
        t.Logf("处理失败: %v, input: %v", err, input)
        return
    }

    // 验证结果
    if result == nil {
        t.Error("结果为nil")
    }
})
```

## 故障排除

### 常见问题

1. **模糊测试没有输出**
   ```
   检查build tag: //go:build fuzz
   ```

2. **测试运行缓慢**
   ```
   使用 -parallel 参数增加工作线程
   或者减少测试时长
   ```

3. **内存不足**
   ```
   添加输入大小限制
   增加跳过条件
   ```

4. **测试超时**
   ```
   添加超时检查
   使用 -fuzztime 参数设置更长的测试时间
   ```

### 调试技巧

1. **查看种子文件**
   ```bash
   go test -tags fuzz ./obs -fuzz=FuzzFunction -fuzzoutput=./corpus/
   ```

2. **分析崩溃文件**
   ```bash
   cat crash-*.txt
   ```

3. **使用小输入范围测试**
   ```bash
   # 限制输入长度
   go test -tags fuzz ./obs -fuzz=FuzzFunction -fuzztime=10s
   ```

## 注意事项

1. **性能影响**：模糊测试会消耗大量CPU和内存资源
2. **测试时间**：建议单独运行，不要与其他测试一起
3. **敏感数据**：避免在生产环境运行模糊测试
4. **覆盖率**：关注代码覆盖率，确保测试有效

## 并行执行模式

本技能支持并行执行模式，可同时为多个目标函数进行模糊测试，显著提升测试效率。

### 启用并行执行

#### 方式1：通过配置启用
```yaml
# 在配置文件中设置
subagent:
  enabled: true
  parallel_workers: 8  # 模糊测试可以更多worker
```

#### 方式2：通过命令行启用
```bash
/go-sdk-fuzz --parallel
/go-sdk-fuzz --parallel --workers=8
/go-sdk-fuzz --targets=xml,url,auth --parallel
```

### 并行执行的工作原理

当启用并行执行时，技能会：

1. **目标分解**：将目标函数分配到不同的 Subagents
2. **并行模糊测试**：同时为多个目标函数运行模糊测试
3. **实时监控**：监控每个模糊测试的进度和资源使用
4. **崩溃收集**：统一收集和分析所有目标的崩溃报告

### 并行执行配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `parallel_workers` | 4 | 并行模糊测试目标数 |
| `fuzz_duration` | 30s | 每个目标的测试时长 |
| `max_inputs_per_target` | 100000 | 每个目标的最大输入数 |
| `memory_limit_per_worker` | 1GB | 每个worker的内存限制 |

### 进度报告

并行执行模式下，技能会实时报告进度：

```
[Fuzzing] go-sdk-fuzz:xml-parser 进度: 50% (inputs: 50000/100000)
[Fuzzing] go-sdk-fuzz:url-parser 进度: 60% (inputs: 60000/100000)
[Fuzzing] go-sdk-fuzz:auth-signature 进度: 30% (inputs: 30000/100000)
[Fuzzing] 崩溃检测: 发现 2 个潜在漏洞
[Fuzzing] 所有目标模糊测试完成
```

### 结果聚合

并行执行完成后，技能会生成统一的测试报告：

```json
{
  "total_targets": 8,
  "total_executions": 800000,
  "total_crashes": 5,
  "unique_crashes": 3,
  "execution_time": "300s",
  "targets": [
    {
      "name": "xml-parser",
      "function": "TransToXml",
      "executions": 100000,
      "crashes": 2,
      "unique_crashes": 1,
      "coverage": 95.2
    },
    {
      "name": "url-parser",
      "function": "parseObsUrl",
      "executions": 100000,
      "crashes": 1,
      "unique_crashes": 1,
      "coverage": 88.5
    },
    ...
  ]
}
```

### 性能对比

| 模式 | 目标数 | 总耗时 | 资源利用率 |
|------|--------|--------|-----------|
| 串行执行 | 8 | 400s | 低 (单核) |
| 并行执行 (4 workers) | 8 | 110s | 中 (4核) |
| 并行执行 (8 workers) | 8 | 60s | 高 (8核) |

**性能提升**：60-75% 的时间减少

### 并行模糊测试策略

#### 1. 目标分组策略

根据函数类型和风险等级分组：

- **高风险组**：XML解析、签名验证（最高优先级）
- **中风险组**：URL解析、输入验证
- **低风险组**：响应解析、辅助函数

#### 2. 资源分配策略

- **CPU密集型**：XML解析、签名验证（分配更多CPU时间）
- **内存密集型**：大文件处理（限制内存使用）
- **I/O密集型**：网络相关（控制并发数）

#### 3. 种子文件管理

每个目标使用独立的种子文件：

```
seeds/
├── xml_parser/
│   ├── valid.xml
│   ├── invalid.xml
│   └── boundary.xml
├── url_parser/
│   ├── valid_urls.txt
│   └── invalid_urls.txt
└── auth_signature/
    ├── valid_auth.txt
    └── invalid_auth.txt
```

### 崩溃分析和优先级

并行执行时会自动分析崩溃并设置优先级：

```json
{
  "crash_priority": {
    "critical": 1,  // 导致程序崩溃
    "high": 2,      // 导致程序异常
    "medium": 3,    // 可能的安全问题
    "low": 4        // 边界条件问题
  }
}
```

### 并行执行最佳实践

1. **合理设置worker数**：根据CPU核心数设置，避免资源争抢
2. **内存限制**：为每个worker设置合理的内存限制
3. **监控资源使用**：实时监控CPU和内存使用情况
4. **崩溃隔离**：一个目标的崩溃不应影响其他目标的测试
5. **结果聚合**：统一分析所有目标的崩溃报告

### 故障恢复

如果某个目标的模糊测试失败：

- 自动记录错误信息
- 其他目标继续执行
- 最终报告包含所有目标的结果
- 支持重新运行失败的目标

## 技能版本

- 版本：1.1.0
- 最后更新：2024-01-09
- 兼容性：OBS SDK v3.x
- Go版本：1.18+ (支持模糊测试)
- **支持技能调用**: 可被go-sdk-dev-task技能调用和协调

## 技能调用接口

本技能可以被go-sdk-dev-task技能调用，以实现开发任务的自动化安全测试。

### 调用方式

go-sdk-dev-task可以通过以下方式调用本技能：

```bash
# 基本调用（使用默认参数）
/go-sdk-dev-task --type=security

# 指定模糊测试目标
/go-sdk-dev-task --fuzz-targets=xml,url,auth

# 指定测试时长
/go-sdk-dev-task --fuzz-duration=60s
```

### 技能协调机制

1. **安全优先策略**
   - 优先为安全关键函数生成模糊测试
   - 识别潜在的输入验证漏洞
   - 检测SQL注入、XSS、XML注入等攻击

2. **去重检查**
   - 检查目标函数是否已有模糊测试
   - 避免重复生成相同测试用例
   - 采用一致的测试命名规范

3. **资源管理**
   - 使用统一的测试语料库目录
   - 避免模糊测试资源冲突
   - 协调崩溃报告存储位置

4. **进度同步**
   - 向go-sdk-dev-task报告模糊测试生成进度
   - 汇总模糊测试结果
   - 识别待解决的安全问题