# go-sdk-dev-task 使用示例

本文档提供了 `go-sdk-dev-task` 技能的实际使用示例。

---

## 技能位置

```
~/.claude/plugins/skills/go-sdk-dev-task/
```

---

## 示例 1: 新功能开发

### 用户输入

```
我需要在 OBS Go SDK 中添加一个新功能：批量删除对象。用户希望能够一次性删除多个对象，提高删除效率。需要支持批量删除 API，包括请求参数设计、响应结构定义、错误处理等。
```

### 技能触发

当用户提到以下关键词时，技能会自动触发：
- "添加新功能"
- "开发新功能"
- "批量删除"
- "如何组织开发工作"
- "任务分解"
- "需要规划"

### 技能输出

技能会自动生成以下文件结构：

```
work-directory/
├── SUBTASKS.md                    # 主任务文件
├── README.md                      # 使用说明
└── subtasks/
    ├── task-01/                   # 设计阶段
    │   ├── TASK.md               # 任务详细描述
    │   ├── IMPLEMENTATION.md       # 实施计划
    │   ├── TEST_PLAN.md          # 测试计划
    │   └── STATUS                # 状态标记
    ├── task-02/                   # 实现阶段
    │   ├── TASK.md
    │   ├── IMPLEMENTATION.md
    │   ├── TEST_PLAN.md
    │   └── STATUS
    ├── task-03/                   # 测试阶段
    │   ├── TASK.md
    │   ├── IMPLEMENTATION.md
    │   ├── TEST_PLAN.md
    │   └── STATUS
    └── task-04/                   # 验收阶段
        ├── TASK.md
        ├── IMPLEMENTATION.md
        ├── TEST_PLAN.md
        └── STATUS
```

### SUBTASKS.md 示例

```markdown
# 任务名称：为 ObsClient 添加批量删除对象功能

## 任务描述
需要支持批量删除 API，包括请求参数设计、响应结构定义、错误处理等。

## 子任务列表
1. 子任务 1 - 设计阶段
2. 子任务 2 - 实现阶段
3. 子任务 3 - 测试阶段
4. 子任务 4 - 验收阶段

## 总体进度
- [ ] 子任务 1 - 设计阶段
- [ ] 子任务 2 - 实现阶段
- [ ] 子任务 3 - 测试阶段
- [ ] 子任务 4 - 验收阶段
```

### 子任务示例

**task-01/TASK.md**:
```markdown
# 子任务编号：设计阶段

## 目标
设计批量删除对象的 API 接口和数据结构

## 范围
- 包含内容：API 设计、数据结构定义、XML 序列化逻辑
- 不包含内容：代码实现、测试编写

## 预估时间
- 工作量：1 天
- 风险缓冲：0.5 天

## 状态
pending
```

**task-03/TEST_PLAN.md**（关键部分）:
```markdown
# 测试计划：批量删除对象功能

## 与 go-sdk-ut skill 集成

### 测试阶段
**必须调用** `/go-sdk-ut` skill 编写单元测试：

1. 使用 /go-sdk-ut skill 编写单元测试
   - 测试命名：Should_ExpectedResult_When_Condition_Given_State
   - 使用 testify 进行断言
   - 使用 httptest 模拟 HTTP 服务器
   - 使用 gomonkey 进行 mock

2. 运行测试：`go test ./obs -v`
3. 检查覆盖率：`go test ./obs -cover`
```

---

## 示例 2: Bug 修复

### 用户输入

```
修复 PutObject 在大文件上传时的内存泄漏问题。上传 5GB 大文件时，内存占用持续增长，最终导致 OOM。需要定位内存泄漏的根源，修复问题，并添加测试验证。
```

### 技能输出特点

对于 Bug 修复任务，技能会生成：

1. **问题分析子任务**：
   - 定位内存泄漏的根本原因
   - 分析受影响的代码路径
   - 识别所有潜在的泄漏点

2. **修复实施子任务**：
   - 修复所有识别的泄漏点
   - 使用 defer 确保资源释放
   - 添加资源管理机制

3. **测试验证子任务**：
   - 编写内存泄漏专项测试
   - 使用 runtime/pprof 进行内存分析
   - 验证修复效果

### TEST_PLAN.md 中的 /go-sdk-ut 集成

```markdown
## 与 go-sdk-ut skill 集成

### 测试阶段
**必须调用** `/go-sdk-ut` skill 编写单元测试：

1. 使用 /go-sdk-ut skill 编写单元测试
   - 测试命名：ShouldNotLeakMemory_WhenUploadingLargeFile
   - 使用 testify 进行断言
   - 使用 httptest 模拟大文件上传
   - 使用 gomonkey mock 文件操作

2. 编写内存泄漏专项测试：
   ```go
   // 测试大文件上传时的内存占用
   func TestPutObject_ShouldNotLeakMemory_WhenUploading5GBFile() {
       // 使用 pprof 监控内存
   }
   ```

3. 运行内存分析：
   ```bash
   go test -memprofile=mem.prof ./obs
   go tool pprof -text mem.prof
   ```
```

---

## 示例 3: 代码重构

### 用户输入

```
重构 auth.go 中的签名逻辑。当前签名逻辑分散在 auth.go、authV2.go 和 authV4.go 中，代码重复且难以维护。需要提取公共逻辑，统一签名接口，提高代码可维护性。
```

### 技能输出特点

对于重构任务，技能会生成：

1. **架构设计子任务**：
   - 分析现有签名逻辑
   - 设计统一的 Signer 接口
   - 定义工厂模式

2. **代码重构子任务**：
   - 实现统一的 Signer 接口
   - 提取公共函数
   - 重构现有签名实现

3. **测试迁移子任务**：
   - 迁移现有测试
   - 编写新的测试用例
   - 确保向后兼容性

4. **验收测试子任务**：
   - 运行完整测试套件
   - 验证性能无退化
   - 检查向后兼容性

### 幂等性保证

技能会在每个子任务目录中创建 `STATUS` 文件：

```bash
# 子任务未开始
subtasks/task-01/STATUS: pending

# 子任务进行中
subtasks/task-01/STATUS: in_progress

# 子任务已完成
subtasks/task-01/STATUS: completed
```

在执行前，可以检查状态：

```python
# 使用内置脚本检查状态
python ~/.claude/plugins/skills/go-sdk-dev-task/scripts/update_task_status.py \
    --task-path subtasks/task-01 \
    --check
```

---

## 状态管理

### 更新子任务状态

```bash
# 使用脚本更新状态
python ~/.claude/plugins/skills/go-sdk-dev-task/scripts/update_task_status.py \
    --task-path subtasks/task-01 \
    --status completed
```

### 手动更新状态

```bash
# 更新为进行中
echo "in_progress" > subtasks/task-01/STATUS

# 更新为已完成
echo "completed" > subtasks/task-01/STATUS
```

---

## 验收报告

完成子任务后，生成验收报告：

```bash
# 使用简化模板生成验收报告（推荐）
cp ~/.claude/plugins/skills/go-sdk-dev-task/templates/acceptance_report_simple.md \
   subtasks/task-01/ACCEPTANCE_REPORT.md
```

### 验收报告示例

```markdown
# 子任务验收报告：设计阶段

**生成时间**：2026-03-05 22:00

## 完成情况总结

### 实现内容
完成了批量删除 API 的接口设计，包括：
- DeleteObjectsInput 数据结构
- DeleteObjectsOutput 数据结构
- ObjectToDelete 辅助结构

### 解决的问题
- 明确了批量删除的请求格式
- 设计了 Quiet 模式支持
- 确定了 URL 编码处理方式

## 测试结果

### go-sdk-ut skill 集成
- **是否调用**：是
- **测试用例数量**：5
- **测试覆盖率**：85%
- **所有测试是否通过**：是

## 代码质量检查

- [ ] 符合 Go 代码规范
- [ ] 通过 golint 检查
- [ ] 通过 go vet 检查
- [ ] 无明显的性能问题
- [ ] 错误处理完善

## 验收结论

- [x] 通过：所有标准已满足

---

## 工作流程

### 完整的开发流程

1. **任务分解**（使用技能）
   - 技能自动识别任务类型
   - 生成结构化的子任务分解
   - 创建所有必需的模板文件

2. **按顺序执行子任务**
   ```
   task-01 → task-02 → task-03 → task-04
   ```

3. **状态跟踪**
   - 每个 subtask 目录包含 STATUS 文件
   - 实时更新任务状态
   - 避免重复执行

4. **测试阶段**（关键步骤）
   - **必须调用** `/go-sdk-ut` skill
   - 使用 BDD 命名规范
   - 使用 testify、httptest、gomonkey
   - 确保测试覆盖率 ≥ 80%

5. **验收阶段**
   - 运行完整测试套件
   - 检查代码质量
   - 生成验收报告

---

## 最佳实践

### 1. 工作目录设置

```bash
# 确保在正确的项目目录
cd /Users/xhyan/project/SDKS/huaweicloud-sdk-go-obs

# 验证当前目录
pwd
# 输出应该是：/Users/xhyan/project/SDKS/huaweicloud-sdk-go-obs
```

### 2. 技能触发

**明确触发**：
```
"我需要分解这个开发任务"
"帮我规划一下如何实现这个功能"
"这个任务太大了，怎么拆分成小任务"
"需要系统性规划这个重构任务"
```

**自动触发**（关键词）：
```
"任务分解"
"任务规划"
"拆分任务"
"子任务"
"开发流程"
"需要规划"
"如何组织"
```

**不应该触发**（简单任务）：
```
"帮我写一个单元测试"  → 应该使用 /go-sdk-ut skill
"怎么用 testify"  → 这是文档查询
"PutObject 怎么用"  → 这是文档查询
"修复这个函数的类型错误"  → 这是简单修复
```

### 3. 子任务执行

```bash
# 开始第一个子任务
cd subtasks/task-01
cat TASK.md              # 查看任务描述
echo "in_progress" > STATUS  # 更新状态

# 完成后
echo "completed" > STATUS    # 更新状态

# 继续下一个子任务
cd ../task-02
```

### 4. 测试编写（关键）

```bash
# 在测试阶段，必须调用 /go-sdk-ut skill

# 示例：
/go-sdk-ut 为批量删除功能编写单元测试，重点测试：
1. 批量删除多个对象
2. Quiet 模式
3. URL 编码处理
4. 错误处理

# 技能会确保：
# - BDD 命名：Should_xxx_When_xxx_Given_xxx
# - 使用 testify、httptest、gomonkey
# - 测试覆盖率 ≥ 80%
```

### 5. 验收检查清单

每个子任务完成后，检查：

```bash
# 功能验收
- [ ] 代码通过所有测试
- [ ] 测试覆盖率达标（建议 >80%）
- [ ] 核心功能正常工作

# 质量验收
- [ ] 符合 Go 代码规范
- [ ] 通过 golint 检查
- [ ] 通过 go vet 检查
- [ ] 无明显的性能问题

# 文档验收
- [ ] 公开 API 有完整的注释
- [ ] 代码注释清晰
- [ ] 示例代码已更新

# /go-sdk-ut 集成检查
- [ ] 在测试阶段调用了 /go-sdk-ut skill
- [ ] 测试命名符合 BDD 规范
- [ ] 使用了正确的测试工具
```

---

## 故障排查

### 常见问题

**Q: 技能没有触发**

A: 检查以下内容：
1. 工作目录是否正确（应在 `/Users/xhyan/project/SDKS/huaweicloud-sdk-go-obs`）
2. 提示是否包含触发关键词
3. 任务是否确实复杂（简单任务不应该触发）

**Q: 子任务文件缺失**

A: 运行以下命令：
```bash
# 检查技能文件
ls -la ~/.claude/plugins/skills/go-sdk-dev-task/

# 重新触发技能，生成完整的子任务
```

**Q: 测试阶段没有明确调用 /go-sdk-ut skill**

A: 检查 TEST_PLAN.md，确保包含：
```markdown
## 与 go-sdk-ut skill 集成

### 测试阶段
**必须调用** `/go-sdk-ut` skill 编写单元测试
```

**Q: STATUS 文件不工作**

A: 使用脚本更新：
```bash
python ~/.claude/plugins/skills/go-sdk-dev-task/scripts/update_task_status.py \
    --task-path subtasks/task-01 \
    --status completed
```

---

## 参考资源

- 技能文档：`~/.claude/plugins/skills/go-sdk-dev-task/SKILL.md`
- 项目约定：`/Users/xhyan/project/SDKS/huaweicloud-sdk-go-obs/CLAUDE.md`
- 测试技能：`/go-sdk-ut` skill
- Go 测试：https://go.dev/doc/tutorial/add-a-test
- BDD 模式：https://martinfowler.com/bliki/GivenWhenThen.html

---

**文档版本**：1.1
**最后更新**：2026-03-05
**技能版本**：1.1
