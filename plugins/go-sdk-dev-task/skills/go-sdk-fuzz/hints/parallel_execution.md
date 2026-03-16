---
title: 模糊测试并行执行
description: 使用 Subagent Manager 实现模糊测试的并行执行，同时为多个目标函数进行模糊测试
---

# 模糊测试并行执行提示词

## 概述

本提示词指导如何使用 Subagent Manager 实现模糊测试的并行执行。通过同时为多个目标函数运行模糊测试，可以显著提升测试覆盖率，更快发现潜在漏洞。

## 启用条件

当满足以下条件时，启用模糊测试的并行执行：

1. 目标函数数量超过 3 个
2. 配置中启用了 `subagent.enabled`
3. 有足够的计算资源（建议 4 核以上）
4. 需要快速完成模糊测试任务

## 实施步骤

### 1. 目标函数识别

识别需要模糊测试的关键函数：

```python
target_functions = [
    'TransToXml',      # XML 解析函数
    'XmlToTrans',      # XML 解析函数
    'parseObsUrl',     # URL 解析函数
    'calculateSignatureV4',  # 签名验证函数
    'parseResponse',   # 响应解析函数
]
```

### 2. 创建 Subagent Manager

```python
from skills.common import SubagentManagerFactory, Config

config = Config()
config.set('subagent.enabled', True)
config.set('subagent.parallel_workers', 8)  # 模糊测试可以使用更多 workers
config.set('subagent.fuzz_duration', 30)

manager = SubagentManagerFactory.create_manager(config)
manager.start()
```

### 3. 并行启动模糊测试

```python
for i, target in enumerate(target_functions):
    agent_id = manager.create_subagent(
        skill_id='go-sdk-fuzz',
        task_id=f'fuzz-target-{i}',
        metadata={
            'target_function': target,
            'duration': 30,
            'max_inputs': 100000
        }
    )

    # 启动模糊测试
    def execute_fuzz(context):
        return run_fuzz_test(context['target'], context['duration'])

    manager.start_subagent(agent_id, execute_fuzz)
```

### 4. 实时监控

注册消息回调，实时监控进度：

```python
def on_status(message: SubagentMessage):
    payload = message.payload
    print(f"[Fuzzing] {message.task_id}: "
          f"{payload.get('status')} "
          f"({payload.get('progress', 0)*100:.1f}%) "
          f"inputs: {payload.get('inputs_executed', 0)}")

manager.register_message_callback(MessageType.STATUS, on_status)
```

### 5. 崩溃报告收集

汇总所有目标的崩溃报告：

```python
results = manager.wait_for_all_subagents(
    skill_id="go-sdk-fuzz",
    task_id="fuzz-target-0",
    timeout=1800.0
)

crash_reports = []
for agent_id, result in results.items():
    if result and result.get('crashes_found', 0) > 0:
        crash_reports.append({
            'agent_id': agent_id,
            'target': result['target_function'],
            'crashes': result['crashes_found'],
            'unique_crashes': result['unique_crashes']
        })
```

## 进度报告示例

```
[Fuzzing] go-sdk-fuzz:xml-parser 进度: 50% (inputs: 50000/100000)
[Fuzzing] go-sdk-fuzz:url-parser 进度: 60% (inputs: 60000/100000)
[Fuzzing] go-sdk-fuzz:auth-signature 进度: 30% (inputs: 30000/100000)
[Fuzzing] 崩溃检测: 发现 2 个潜在漏洞
[Fuzzing] 所有目标模糊测试完成
```

## 崩溃分析策略

### 1. 崩溃优先级

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

### 2. 崩溃去重

识别和合并重复的崩溃：

```python
def deduplicate_crashes(crash_reports):
    unique_crashes = {}
    for report in crash_reports:
        crash_signature = generate_crash_signature(report['stack_trace'])
        if crash_signature not in unique_crashes:
            unique_crashes[crash_signature] = report
    return list(unique_crashes.values())
```

### 3. 根因分析

对每个崩溃进行根本原因分析：

```json
{
  "crash": {
    "function": "TransToXml",
    "input": "malicious XML input",
    "stack_trace": "...",
    "root_cause": "XML 解析未对恶意输入进行验证",
    "recommendation": "添加 XML 输入验证"
  }
}
```

## 资源管理

### 1. 内存限制

为每个模糊测试任务设置内存限制：

```python
memory_limit_per_worker = 1 * 1024 * 1024 * 1024  # 1GB

def execute_fuzz_with_memory_limit(context):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_per_worker, memory_limit_per_worker))
    return run_fuzz_test(context['target'], context['duration'])
```

### 2. CPU 亲和性

将不同的模糊测试任务绑定到不同的 CPU 核心：

```python
import os

for i, task in enumerate(tasks):
    os.sched_setaffinity(0, {i % cpu_count})  # 绑定到特定 CPU 核心
    manager.start_subagent(agent_id, execute_func)
```

### 3. 超时控制

为每个目标函数设置独立的超时：

```python
timeout_per_target = min(context['duration'], 60)  # 最多 60 秒

try:
    result = run_fuzz_test_with_timeout(target, timeout_per_target)
except TimeoutError:
    logger.warning(f"模糊测试超时: {target}")
```

## 种子文件管理

### 1. 种子文件组织

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

### 2. 种子文件加载

为每个目标加载对应的种子文件：

```python
def load_seeds_for_target(target):
    seeds_dir = Path('seeds') / target.lower().replace('_', '-')
    seeds = []
    if seeds_dir.exists():
        for seed_file in seeds_dir.glob('*'):
            with open(seed_file, 'r') as f:
                seeds.append(f.read())
    return seeds
```

## 性能优化建议

### 1. Worker 数量优化

- 小型项目（< 5 个目标）：4-6 个 workers
- 中型项目（5-10 个目标）：6-8 个 workers
- 大型项目（> 10 个目标）：8-12 个 workers

### 2. 输入生成优化

使用高效的输入生成策略：
- 基于种子的随机生成
- 基于变异的生成
- 基于语法的生成

### 3. 并行化策略

- 数据并行：不同的 targets 并行执行
- 输入并行：同一个 target 的不同输入并行
- 混合并行：同时使用两种策略

## 错误恢复

### 1. 崩溃恢复

当模糊测试崩溃时：
- 记录崩溃输入
- 保存崩溃现场
- 自动重启模糊测试
- 跳过崩溃输入

### 2. 超时恢复

当测试超时时：
- 减少输入大小
- 降低复杂度
- 跳过耗时的输入
- 调整测试参数

### 3. 资源不足恢复

当资源不足时：
- 减少 worker 数量
- 降低内存限制
- 优化输入生成
- 分批执行

## 最佳实践

1. **风险优先**：优先测试高风险函数
2. **覆盖优先**：确保测试覆盖率充足
3. **记录完整**：详细记录每个崩溃
4. **定期报告**：定期生成崩溃报告
5. **持续优化**：根据反馈优化模糊测试策略

## 示例命令

```bash
# 启用并行模糊测试
/go-sdk-fuzz --parallel

# 指定目标函数
/go-sdk-fuzz --targets=xml,url,auth --parallel

# 设置测试时长
/go-sdk-fuzz --duration=60 --parallel --workers=8

# 使用种子文件
/go-sdk-fuzz --seeds=./fuzz_seeds/ --parallel
```

## 注意事项

1. **安全优先**：优先测试安全关键函数
2. **资源充足**：确保有足够的计算资源
3. **存储空间**：保留足够的磁盘空间保存崩溃报告
4. **网络隔离**：避免模糊测试影响生产环境
5. **结果验证**：验证发现的漏洞是否真实可利用
