---
title: 集成测试并行执行
description: 使用 Subagent Manager 实现集成测试的并行执行，同时运行多个测试模块
---

# 集成测试并行执行提示词

## 概述

本提示词指导如何使用 Subagent Manager 实现集成测试的并行执行。通过同时运行多个集成测试模块（如认证、Bucket操作、对象操作），可以快速验证核心功能的端到端流程。

## 启用条件

当满足以下条件时，启用集成测试的并行执行：

1. 需要测试多个集成模块
2. 模块之间没有强依赖关系
3. 配置中启用了 `subagent.enabled`
4. 有多个独立的测试环境

## 实施步骤

### 1. 测试模块定义

定义要测试的集成模块：

```python
integration_modules = [
    {
        'name': 'auth-module',
        'description': '认证测试模块',
        'dependencies': [],
        'environment': 'test-env-1'
    },
    {
        'name': 'bucket-module',
        'description': 'Bucket 操作测试模块',
        'dependencies': ['auth-module'],
        'environment': 'test-env-2'
    },
    {
        'name': 'object-module',
        'description': '对象操作测试模块',
        'dependencies': ['auth-module', 'bucket-module'],
        'environment': 'test-env-3'
    },
    {
        'name': 'multipart-module',
        'description': '分块上传测试模块',
        'dependencies': ['auth-module', 'bucket-module', 'object-module'],
        'environment': 'test-env-4'
    }
]
```

### 2. 创建 Subagent Manager

```python
from skills.common import SubagentManagerFactory, Config

config = Config()
config.set('subagent.enabled', True)
config.set('subagent.parallel_workers', 3)
config.set('subagent.test_timeout', 300)
config.set('subagent.cleanup_timeout', 60)

manager = SubagentManagerFactory.create_manager(config)
manager.start()
```

### 3. 模块分组和调度

根据依赖关系对模块分组：

```python
def schedule_modules(modules):
    """根据依赖关系调度模块"""
    # 无依赖组：可并行执行
    no_deps = [m for m in modules if not m['dependencies']]

    # 部分依赖组：部分顺序约束
    partial_deps = [m for m in modules if m['dependencies']]

    # 完全依赖组：完全顺序执行
    full_deps = sorted(
        [m for m in modules if len(m['dependencies']) > 2],
        key=lambda x: len(x['dependencies'])
    )

    return {
        'parallel': no_deps,
        'sequential': partial_deps + full_deps
    }

scheduled = schedule_modules(integration_modules)
```

### 4. 并行执行无依赖模块

```python
# 并行执行无依赖模块
for i, module in enumerate(scheduled['parallel']):
    agent_id = manager.create_subagent(
        skill_id='go-sdk-integration',
        task_id=f'integration-{module["name"]}',
        metadata={
            'module': module['name'],
            'environment': module['environment']
        }
    )

    def execute_integration(context):
        return run_integration_tests(
            module=module['name'],
            environment=module['environment']
        )

    manager.start_subagent(agent_id, execute_integration)
```

### 5. 顺序执行有依赖模块

```python
# 顺序执行有依赖模块
for i, module in enumerate(scheduled['sequential']):
    # 等待依赖模块完成
    dependencies = module['dependencies']
    for dep in dependencies:
        wait_for_module_completion(dep)

    # 执行当前模块
    agent_id = manager.create_subagent(
        skill_id='go-sdk-integration',
        task_id=f'integration-{module["name"]}',
        metadata={
            'module': module['name'],
            'environment': module['environment']
        }
    )

    def execute_integration(context):
        return run_integration_tests(
            module=module['name'],
            environment=module['environment']
        )

    manager.start_subagent(agent_id, execute_integration)
```

### 6. 环境隔离

为每个模块创建独立的测试环境：

```python
def setup_test_environment(module_name, environment):
    """设置测试环境"""
    # 创建独立的测试 Bucket
    test_bucket = f"test-{module_name}-{int(time.time())}"

    # 设置环境变量
    os.environ[f'OBS_TEST_BUCKET_{module_name.upper()}'] = test_bucket

    # 如果使用 Mock 服务器，分配不同的端口
    mock_port = 8080 + int(module_name[-1])
    os.environ[f'OBS_MOCK_PORT_{module_name.upper()}'] = str(mock_port)

    return {
        'test_bucket': test_bucket,
        'mock_port': mock_port
    }
```

### 7. 资源清理

确保每个模块完成后清理资源：

```python
def cleanup_test_environment(module_name, environment):
    """清理测试环境"""
    # 清理测试对象
    test_bucket = environment['test_bucket']
    client = get_test_client()

    try:
        # 列出并删除所有对象
        objects = client.ListObjects(test_bucket)
        for obj in objects:
            client.DeleteObject(test_bucket, obj['Key'])

        # 删除测试 Bucket
        client.DeleteBucket(test_bucket)

    except Exception as e:
        logger.error(f"清理失败: {e}")
        raise
```

## 进度报告示例

```
[Integration] go-sdk-integration:auth-module 进度: 80% (tests: 8/10)
[Integration] go-sdk-integration:bucket-module 进度: 60% (tests: 6/10)
[Integration] go-sdk-integration:object-module 进度: 40% (tests: 4/10)
[Integration] go-sdk-integration:multipart-module 进度: 20% (tests: 2/10)
[Integration] auth-module 完成 (passed: 9/10, failed: 1/10)
[Integration] bucket-module 完成 (passed: 8/8, failed: 0/8)
[Integration] object-module 完成 (passed: 15/15, failed: 0/15)
[Integration] multipart-module 完成 (passed: 5/5, failed: 0/5)
[Integration] 所有模块测试完成
[Integration] 正在生成汇总报告...
```

## 汇总报告生成

### 1. 模块测试结果

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "execution_time": "300s",
  "modules": [
    {
      "name": "auth-module",
      "tests_total": 10,
      "tests_passed": 9,
      "tests_failed": 1,
      "tests_skipped": 0,
      "execution_time": "85s",
      "cleanup_time": "5s",
      "status": "partial_failure"
    },
    {
      "name": "bucket-module",
      "tests_total": 8,
      "tests_passed": 8,
      "tests_failed": 0,
      "tests_skipped": 0,
      "execution_time": "72s",
      "cleanup_time": "3s",
      "status": "passed"
    },
    {
      "name": "object-module",
      "tests_total": 15,
      "tests_passed": 15,
      "tests_failed": 0,
      "tests_skipped": 0,
      "execution_time": "95s",
      "cleanup_time": "8s",
      "status": "passed"
    },
    {
      "name": "multipart-module",
      "tests_total": 5,
      "tests_passed": 5,
      "tests_failed": 0,
      "tests_skipped": 0,
      "execution_time": "60s",
      "cleanup_time": "5s",
      "status": "passed"
    }
  ],
  "summary": {
    "total_modules": 4,
    "total_tests": 38,
    "total_passed": 37,
    "total_failed": 1,
    "total_skipped": 0,
    "overall_status": "partial_failure",
    "success_rate": "97.4%"
  }
}
```

### 2. 端到端流程验证

```json
{
  "end_to_end_workflows": [
    {
      "name": "upload-download-workflow",
      "modules": ["auth-module", "bucket-module", "object-module"],
      "status": "passed",
      "total_time": "252s"
    },
    {
      "name": "multipart-upload-workflow",
      "modules": ["auth-module", "bucket-module", "object-module", "multipart-module"],
      "status": "passed",
      "total_time": "312s"
    }
  ]
}
```

## Mock 服务器管理

### 1. 并行 Mock 服务器

为每个模块启动独立的 Mock 服务器：

```python
def start_mock_servers(modules):
    """启动并行 Mock 服务器"""
    mock_servers = {}

    for module in modules:
        port = 8080 + int(module['name'][-1])
        mock_server = MockServer(port)
        mock_server.start()
        mock_servers[module['name']] = {
            'server': mock_server,
            'port': port,
            'url': f'http://localhost:{port}'
        }

    return mock_servers
```

### 2. Mock 服务器配置

配置 Mock 服务器的行为：

```python
def configure_mock_server(server, module_name):
    """配置 Mock 服务器"""
    if module_name == 'auth-module':
        server.configure({
            'responses': {
                '/location': {'status': 200, 'body': 'mock_location'},
                '/credential': {'status': 200, 'body': 'mock_credential'}
            }
        })
    elif module_name == 'bucket-module':
        server.configure({
            'responses': {
                '/create-bucket': {'status': 200},
                '/delete-bucket': {'status': 204},
                '/list-buckets': {'status': 200, 'body': '[]'}
            }
        })
    # ... 其他模块配置
```

## 错误处理和恢复

### 1. 模块失败处理

当某个模块失败时：

```python
def handle_module_failure(module_name, error):
    """处理模块失败"""
    logger.error(f"模块 {module_name} 失败: {error}")

    # 记录失败信息
    failure_report = {
        'module': module_name,
        'error': str(error),
        'timestamp': datetime.now().isoformat(),
        'stack_trace': traceback.format_exc()
    }

    # 保存失败报告
    save_failure_report(failure_report)

    # 尝试清理资源
    try:
        cleanup_test_environment(module_name, get_environment(module_name))
    except Exception as cleanup_error:
        logger.error(f"清理失败: {cleanup_error}")
```

### 2. 依赖失败处理

当依赖模块失败时：

```python
def handle_dependency_failure(module, failed_dependencies):
    """处理依赖失败"""
    logger.warning(f"模块 {module['name']} 的依赖失败: {failed_dependencies}")

    # 标记模块为跳过
    skip_report = {
        'module': module['name'],
        'status': 'skipped',
        'reason': f'依赖模块失败: {failed_dependencies}',
        'timestamp': datetime.now().isoformat()
    }

    return skip_report
```

### 3. 部分恢复策略

即使部分模块失败，继续执行其他模块：

```python
def execute_with_partial_recovery(modules):
    """部分恢复策略执行"""
    completed_modules = []
    failed_modules = []

    for module in modules:
        try:
            # 执行模块
            result = execute_module(module)
            completed_modules.append(result)

        except Exception as e:
            # 记录失败
            failed_modules.append({
                'module': module['name'],
                'error': str(e)
            })

            # 如果不是关键依赖，继续执行其他模块
            if not is_critical_dependency(module):
                continue
            else:
                # 如果是关键依赖，停止执行
                break

    return {
        'completed': completed_modules,
        'failed': failed_modules
    }
```

## 最佳实践

### 1. 依赖管理

- 明确定义模块依赖关系
- 优先执行无依赖模块
- 合理处理依赖失败

### 2. 环境隔离

- 每个模块使用独立的测试环境
- 避免测试资源冲突
- 确保模块之间互不影响

### 3. 资源清理

- 每个模块完成后立即清理
- 使用清理函数和注册机制
- 确保清理失败不影响其他模块

### 4. 错误隔离

- 一个模块的失败不应影响其他模块
- 记录详细的错误信息
- 提供清晰的失败原因

### 5. 结果汇总

- 统一汇总所有模块的结果
- 生成端到端流程验证报告
- 提供清晰的成功率统计

## 示例命令

```bash
# 启用并行集成测试
/go-sdk-integration --parallel

# 指定测试模块
/go-sdk-integration --modules=auth,bucket,object --parallel

# 设置并行工作数
/go-sdk-integration --parallel --workers=3

# 使用 Mock 服务器
/go-sdk-integration --mock-enabled=true --parallel
```

## 注意事项

1. **依赖分析**：确保正确识别模块依赖关系
2. **环境配置**：确保测试环境配置正确
3. **资源充足**：确保有足够的测试资源
4. **网络隔离**：避免测试相互干扰
5. **清理验证**：确保测试资源完全清理
