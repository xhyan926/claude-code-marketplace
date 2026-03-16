---
title: 性能测试并行执行
description: 使用 Subagent Manager 实现性能测试的并行执行，同时运行多个性能测试场景
---

# 性能测试并行执行提示词

## 概述

本提示词指导如何使用 Subagent Manager 实现性能测试的并行执行。通过同时运行多个性能测试场景（不同的并发级别、文件大小等），可以快速建立完整的性能基线。

## 启用条件

当满足以下条件时，启用性能测试的并行执行：

1. 需要测试多个性能场景
2. 性能测试数量超过 3 个
3. 配置中启用了 `subagent.enabled`
4. 需要快速完成性能基准测试

## 实施步骤

### 1. 测试场景设计

定义性能测试场景矩阵：

```python
test_scenarios = [
    # 轻量级测试
    {'type': 'light', 'file_size': '1MB', 'concurrency': 10, 'duration': 1},
    {'type': 'light', 'file_size': '1MB', 'concurrency': 50, 'duration': 1},
    {'type': 'light', 'file_size': '1MB', 'concurrency': 100, 'duration': 1},

    # 深度测试
    {'type': 'deep', 'file_size': '100MB', 'concurrency': 10, 'duration': 30},
    {'type': 'deep', 'file_size': '100MB', 'concurrency': 50, 'duration': 30},
    {'type': 'deep', 'file_size': '100MB', 'concurrency': 100, 'duration': 30},

    # 并发测试
    {'type': 'concurrent', 'file_size': '10MB', 'concurrency': 10, 'duration': 10},
    {'type': 'concurrent', 'file_size': '10MB', 'concurrency': 50, 'duration': 10},
    {'type': 'concurrent', 'file_size': '10MB', 'concurrency': 100, 'duration': 10},
]
```

### 2. 创建 Subagent Manager

```python
from skills.common import SubagentManagerFactory, Config

config = Config()
config.set('subagent.enabled', True)
config.set('subagent.parallel_workers', 4)

manager = SubagentManagerFactory.create_manager(config)
manager.start()
```

### 3. 并行启动性能测试

```python
for i, scenario in enumerate(test_scenarios):
    agent_id = manager.create_subagent(
        skill_id='go-sdk-perf',
        task_id=f'perf-scenario-{i}',
        metadata={
            'scenario': scenario,
            'benchmark_name': generate_benchmark_name(scenario)
        }
    )

    # 启动性能测试
    def execute_benchmark(context):
        scenario = context['scenario']
        return run_performance_benchmark(
            test_type=scenario['type'],
            file_size=scenario['file_size'],
            concurrency=scenario['concurrency'],
            duration=scenario['duration']
        )

    manager.start_subagent(agent_id, execute_benchmark)
```

### 4. 实时资源监控

监控每个性能测试的资源使用：

```python
def monitor_resources(agent_id):
    info = manager.get_subagent_info(agent_id)
    metadata = info.metadata
    print(f"[Performance] {info.task_id}: "
          f"CPU: {metadata.get('cpu_percent', 0)}%, "
          f"Memory: {metadata.get('memory_mb', 0)}MB")

# 定期监控
while not all_completed:
    for agent_id in agent_ids:
        monitor_resources(agent_id)
    time.sleep(5)
```

### 5. 基线对比

与历史基线数据进行对比：

```python
def compare_with_baseline(current_result, historical_baseline):
    throughput_improvement = (
        (current_result['throughput_mb_s'] - historical_baseline['throughput_mb_s']) /
        historical_baseline['throughput_mb_s'] * 100
    )

    return {
        'improvement': throughput_improvement,
        'status': 'improved' if throughput_improvement > 0 else 'degraded',
        'threshold': 10  # 10% 为告警阈值
    }
```

## 进度报告示例

```
[Performance] go-sdk-perf:light-1MB-concurrent-10 进度: 80% (ops: 800/1000)
[Performance] go-sdk-perf:light-1MB-concurrent-50 进度: 60% (ops: 600/1000)
[Performance] go-sdk-perf:deep-100MB-concurrent-10 进度: 40% (ops: 40/100)
[Performance] go-sdk-perf:concurrent-10MB-concurrent-100 进度: 100% (ops: 100/100)
[Performance] 所有基准测试完成
[Performance] 正在生成性能报告...
```

## 性能报告生成

### 1. 测试结果汇总

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "execution_time": "180s",
  "benchmarks": [
    {
      "name": "BenchmarkLight_PutObject_SmallFile",
      "type": "light",
      "file_size": "1MB",
      "concurrency": 10,
      "results": {
        "throughput_mb_s": 175.5,
        "ns_per_op": 5842341,
        "allocs_per_op": 28,
        "baseline": 150.0,
        "status": "ok"
      }
    }
  ],
  "summary": {
    "total_benchmarks": 12,
    "passed": 11,
    "regressions": 1,
    "avg_improvement": "12.5%",
    "max_improvement": "35.2%"
  }
}
```

### 2. 性能趋势分析

```python
def analyze_performance_trend(results):
    """分析性能趋势"""
    throughputs = [r['results']['throughput_mb_s'] for r in results]

    return {
        'min': min(throughputs),
        'max': max(throughputs),
        'avg': sum(throughputs) / len(throughputs),
        'std': calculate_std(throughputs)
    }
```

### 3. 性能退化检测

```python
def detect_regression(current, baseline, threshold=0.1):
    """检测性能退化"""
    degradation = (baseline - current) / baseline

    if degradation > threshold:
        return {
            'detected': True,
            'degradation': degradation * 100,
            'severity': 'high' if degradation > 0.2 else 'medium'
        }

    return {'detected': False}
```

## 资源监控策略

### 1. CPU 监控

```python
import psutil

def monitor_cpu_usage():
    """监控 CPU 使用率"""
    cpu_percent = psutil.cpu_percent(interval=1)
    return {
        'current': cpu_percent,
        'avg': sum(cpu_history) / len(cpu_history),
        'max': max(cpu_history)
    }
```

### 2. 内存监控

```python
def monitor_memory_usage():
    """监控内存使用"""
    mem = psutil.virtual_memory()
    return {
        'used_mb': mem.used / (1024 * 1024),
        'total_mb': mem.total / (1024 * 1024),
        'percent': mem.percent,
        'available_mb': mem.available / (1024 * 1024)
    }
```

### 3. 网络监控

```python
def monitor_network_usage():
    """监控网络使用"""
    net = psutil.net_io_counters()
    return {
        'bytes_sent': net.bytes_sent,
        'bytes_recv': net.bytes_recv,
        'packets_sent': net.packets_sent,
        'packets_recv': net.packets_recv
    }
```

## 测试场景优化

### 1. 场景分组

根据资源需求分组测试场景：

```python
# CPU 密集型组
cpu_intensive = [
    {'type': 'encryption', 'file_size': '1MB', 'concurrency': 100},
    {'type': 'signature', 'file_size': '1MB', 'concurrency': 100},
]

# I/O 密集型组
io_intensive = [
    {'type': 'upload', 'file_size': '100MB', 'concurrency': 10},
    {'type': 'download', 'file_size': '100MB', 'concurrency': 10},
]

# 混合型组
mixed = [
    {'type': 'normal', 'file_size': '10MB', 'concurrency': 50},
]
```

### 2. 负载均衡

确保每个 Subagent 的负载均衡：

```python
def balance_loads(scenarios, num_workers):
    """均衡负载分配"""
    balanced_scenarios = []
    for i, scenario in enumerate(scenarios):
        # 根据 CPU、内存、I/O 需求分配
        worker_id = i % num_workers
        balanced_scenarios.append({
            **scenario,
            'worker_id': worker_id
        })
    return balanced_scenarios
```

### 3. 超时调整

根据测试类型动态调整超时：

```python
def calculate_timeout(scenario):
    """计算合理的超时时间"""
    base_timeout = scenario['duration']
    multiplier = {
        'light': 3,      # 轻量级测试：3倍
        'deep': 2,       # 深度测试：2倍
        'concurrent': 2.5 # 并发测试：2.5倍
    }
    return base_timeout * multiplier.get(scenario['type'], 2)
```

## 性能基线管理

### 1. 基线存储

```json
{
  "baselines": {
    "BenchmarkLight_PutObject_SmallFile": {
      "throughput_mb_s": 150.0,
      "timestamp": "2023-12-01T12:00:00Z",
      "environment": {
        "cpu": "Intel i7",
        "memory": "16GB",
        "network": "1Gbps"
      }
    }
  }
}
```

### 2. 基线更新

定期更新性能基线：

```python
def update_baseline(benchmark_name, new_result):
    """更新性能基线"""
    baseline_file = load_baseline_file()
    old_baseline = baseline_file['baselines'].get(benchmark_name)

    if old_baseline:
        # 计算变化
        change = (new_result['throughput_mb_s'] - old_baseline['throughput_mb_s']) / old_baseline['throughput_mb_s']
        baseline_file['baselines'][benchmark_name]['history'].append({
            'timestamp': old_baseline['timestamp'],
            'throughput': old_baseline['throughput_mb_s']
        })

    # 更新为最新值
    baseline_file['baselines'][benchmark_name] = {
        'throughput_mb_s': new_result['throughput_mb_s'],
        'timestamp': datetime.now().isoformat(),
        'history': baseline_file['baselines'].get(benchmark_name, {}).get('history', [])
    }

    save_baseline_file(baseline_file)
```

### 3. 趋势分析

分析性能趋势：

```python
def analyze_trend(benchmark_name, baseline_file):
    """分析性能趋势"""
    history = baseline_file['baselines'][benchmark_name].get('history', [])

    if len(history) < 2:
        return 'insufficient_data'

    throughputs = [h['throughput'] for h in history]
    recent = throughputs[-3:]  # 最近 3 次

    if len(recent) < 2:
        return 'insufficient_recent_data'

    # 计算趋势
    avg_recent = sum(recent) / len(recent)
    avg_all = sum(throughputs) / len(throughputs)

    if avg_recent > avg_all * 1.05:
        return 'improving'
    elif avg_recent < avg_all * 0.95:
        return 'degrading'
    else:
        return 'stable'
```

## 最佳实践

1. **场景全面**：覆盖不同的文件大小、并发级别
2. **基线对比**：始终与历史基线对比
3. **资源监控**：实时监控 CPU、内存、网络使用
4. **趋势分析**：分析性能趋势，发现潜在问题
5. **告警机制**：设置性能退化告警阈值

## 示例命令

```bash
# 启用并行性能测试
/go-sdk-perf --parallel

# 指定测试类型
/go-sdk-perf --type=light,deep --parallel

# 设置并发级别
/go-sdk-perf --concurrency=10,50,100 --parallel

# 指定文件大小
/go-sdk-perf --sizes=1MB,10MB,100MB --parallel

# 设置测试时长
/go-sdk-perf --duration=30 --parallel --workers=4
```

## 注意事项

1. **环境一致**：确保测试环境一致
2. **网络稳定**：避免网络波动影响结果
3. **资源充足**：确保有足够的硬件资源
4. **数据清理**：每次测试后清理测试数据
5. **结果验证**：验证并行结果的正确性
