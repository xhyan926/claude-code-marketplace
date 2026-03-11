---
name: doc-verifier
description: 文档验证技能，验证文档完整性、用例正确性、编译并运行示例代码，生成 DOC_VERIFICATION.md。
---

# doc-verifier

## 技能用途

本技能用于验证生成的 API 文档和示例代码的正确性。适用于：

- `/sdk-doc` 技能生成文档后的验证
- 子任务完成前的文档质量检查
- 发布前的文档完整性验证

## 前置条件

1. **文档已生成**：API 文档已通过 `/sdk-doc` 技能生成
2. **文档文件存在**：`docs/` 目录下有新的或更新的文档文件
3. **SDK 可访问**：可以导入和测试 SDK

## 验证内容

### 1. 文档完整性

#### 文件存在性检查
- [ ] 文档文件存在
- [ ] 文档索引已更新
- [ ] 示例代码文件存在

#### 内容完整性检查
- [ ] 方法签名准确
- [ ] 参数说明完整
- [ ] 返回值描述准确
- [ ] 错误码列表完整
- [ ] 注意事项清晰

### 2. 格式规范

#### Markdown 格式
- [ ] 标题层级正确
- [ ] 代码块带语言标识
- [ ] 表格格式规范
- [ ] 列表格式正确
- [ ] 链接有效

#### 代码格式
- [ ] 代码缩进正确
- [ ] 变量命名规范
- [ ] 注释完整
- [ ] 导入语句完整

### 3. 示例代码验证

#### 代码编译
- [ ] 所有示例代码可编译
- [ ] 无语法错误
- [ ] 无类型错误

#### 代码运行
- [ ] 示例代码可运行
- [ ] 输出符合预期
- [ ] 无运行时错误

#### API 一致性
- [ ] 示例中的 API 签名与实际代码一致
- [ ] 参数名称和类型匹配
- [ ] 返回值结构正确

### 4. 用例正确性

#### 测试用例
- [ ] 测试场景覆盖完整
- [ ] 测试数据有效
- [ ] 预期结果正确

#### 示例用例
- [ ] 示例场景合理
- [ ] 示例数据有效
- [ ] 示例步骤清晰

## 验证流程

### 第 1 步：文档收集
1. 扫描 `docs/` 目录，识别新增/修改的文档
2. 收集所有示例代码
3. 提取 API 签名信息

### 第 2 步：格式验证
1. 检查 Markdown 格式
2. 验证代码块语法
3. 检查表格格式
4. 验证链接有效性

### 第 3 步：API 一致性验证
1. 读取文档中的 API 签名
2. 查找实际代码中的定义
3. 比对签名、参数、返回值
4. 记录不一致之处

### 第 4 步：示例代码编译
```bash
# 提取示例代码
for doc in docs/**/*.md; do
    extract_example_code $doc > temp_example.go
    go build temp_example.go
done
```

### 第 5 步：示例代码运行
```bash
# 运行示例代码（需要有效的凭证）
for doc in docs/**/*.md; do
    extract_example_code $doc > temp_example.go
    go run temp_example.go
done
```

### 第 6 步：生成验证报告
生成 `DOC_VERIFICATION.md`，包含：
- 验证结果汇总
- 发现的问题列表
- 修复建议
- 验收结论

## 输出格式

### DOC_VERIFICATION.md

```markdown
# 文档验证报告

**验证日期**：{{ .VerificationDate }}
**验证者**：{{ .Verifier }}
**文档范围**：{{ .DocScope }}

## 验证结果汇总

- 验证文档数：{{ .TotalDocs }}
- 通过验证数：{{ .PassedDocs }}
- 需要修改数：{{ .FailedDocs }}
- 验证通过率：{{ .PassRate }}%

## 验收结论

{{- if .IsPassed }}
✓ **通过**：所有文档通过验证
{{- else if .NeedsRevision }}
⚠️ **需要修改**：部分文档需要修改
{{- else }}
✗ **失败**：关键文档验证失败
{{- end }}

## 文档完整性

### 文件存在性
{{- range .FileChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .File }}
{{- end }}

### 内容完整性
{{- range .ContentChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .Check }}
{{- end }}

## 格式规范

### Markdown 格式
{{- range .MarkdownChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .Check }}
{{- end }}

### 代码格式
{{- range .CodeFormatChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .Check }}
{{- end }}

## 示例代码验证

### 编译检查
{{- range .CompilationChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .File }}: {{ .Message }}
{{- end }}

### 运行检查
{{- range .RuntimeChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .File }}: {{ .Message }}
{{- end }}

### API 一致性
{{- range .APIConsistencyChecks }}
- [{{ if .Passed }}✓{{ else }}✗{{ end }}] {{ .API }}: {{ .Message }}
{{- end }}

## 发现的问题

### 严重问题
{{- range .CriticalIssues }}
#### {{ .Title }}
- **文档**：{{ .DocFile }}
- **问题描述**：{{ .Description }}
- **影响**：{{ .Impact }}
- **建议**：{{ .Suggestion }}
{{- end }}

### 一般问题
{{- range .MajorIssues }}
#### {{ .Title }}
- **文档**：{{ .DocFile }}
- **问题描述**：{{ .Description }}
- **建议**：{{ .Suggestion }}
{{- end }}

## 修复建议

{{- range .FixSuggestions }}
1. {{ . }}
{{- end }}

## 下一步

{{- if .IsPassed }}
- [ ] 文档验证通过，可以发布
- [ ] 更新文档版本号
{{- else }}
- [ ] 修复所有严重问题
- [ ] 修复所有一般问题
- [ ] 重新运行验证
- [ ] 更新 DOC_VERIFICATION.md
{{- end }}

---

**最后更新**：{{ .LastUpdated }}
```

## 验证通过条件

满足以下条件时，文档验证通过：

1. 无严重问题
2. 一般问题全部修复或解释清楚
3. 所有示例代码可编译
4. 所有示例代码可运行（或明确说明需要环境）
5. API 签名与实际代码一致

## 注意事项

### 环境要求

- 需要 Go 编译环境
- 需要 SDK 源代码
- 某些示例需要有效的 OBS 凭证

### 验证限制

- 无法验证网络连接（依赖实际环境）
- 无法验证权限问题（依赖实际环境）
- 某些功能需要特定环境才能验证

### 持续集成

建议在 CI/CD 流程中集成文档验证：

```yaml
# .github/workflows/doc-verify.yml
name: Verify Documentation
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Go
        uses: actions/setup-go@v2
        with:
          go-version: '1.x'
      - name: Verify docs
        run: |
          python skills/doc-verifier/scripts/verifier.py
```
