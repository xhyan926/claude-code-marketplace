"""
并行测试执行器

使用 Subagent Manager 实现测试技能的并行执行，显著提升测试效率。
"""

import sys
import os
import json
import time
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.common.subagent_manager import (
    SubagentManager,
    SubagentManagerFactory,
    SubagentInfo
)
from skills.common.config import Config
from skills.common.message_protocol import SubagentState, SubagentMessage, MessageType
from skills.common.logger import get_logger


class ParallelTestExecutor:
    """
    并行测试执行器

    使用 Subagent Manager 并行执行多个测试任务。
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化并行测试执行器

        Args:
            config: 配置对象，如果为 None 则使用默认配置
        """
        self.config = config or Config()
        self.logger = get_logger("ParallelTestExecutor")

        # 创建 Subagent Manager
        self.manager = SubagentManagerFactory.create_manager(self.config)
        self.manager.start()

        # 测试结果
        self.test_results: Dict[str, Any] = {}
        self.test_errors: Dict[str, Exception] = {}

        # 注册消息回调
        self._register_message_callbacks()

    def _register_message_callbacks(self):
        """注册消息回调"""
        def on_status(message: SubagentMessage):
            self.logger.info(
                f"测试进度: {message.skill_id}:{message.task_id} = "
                f"{message.payload.get('status', 'unknown')} "
                f"({message.payload.get('progress', 0)*100:.1f}%)"
            )

        def on_result(message: SubagentMessage):
            self.logger.info(
                f"测试结果: {message.skill_id}:{message.task_id} = "
                f"{message.payload.get('success', False)}"
            )

        def on_error(message: SubagentMessage):
            self.logger.error(
                f"测试错误: {message.skill_id}:{message.task_id} = "
                f"{message.payload.get('error_message', 'Unknown error')}"
            )

        self.manager.register_message_callback(MessageType.STATUS, on_status)
        self.manager.register_message_callback(MessageType.RESULT, on_result)
        self.manager.register_message_callback(MessageType.ERROR, on_error)

    def execute_tests_parallel(
        self,
        test_tasks: List[Dict[str, Any]],
        parallel_workers: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        并行执行多个测试任务

        Args:
            test_tasks: 测试任务列表，每个任务包含：
                - skill_id: 技能标识
                - task_id: 任务标识
                - execute_func: 执行函数
                - metadata: 附加元数据
            parallel_workers: 并行工作数，如果为 None 则使用配置值

        Returns:
            Dict[str, Any]: 所有测试任务的结果
        """
        # 获取并行工作数
        parallel_workers = parallel_workers or self.config.get_parallel_workers()

        self.logger.info(f"启动并行测试执行 (workers: {parallel_workers})")

        # 创建 Subagents
        agent_ids = []
        for task in test_tasks:
            agent_id = self.manager.create_subagent(
                skill_id=task['skill_id'],
                task_id=task['task_id'],
                metadata=task.get('metadata', {})
            )

            # 启动 Subagent
            self.manager.start_subagent(
                agent_id,
                task['execute_func'],
                context=task.get('context', {})
            )

            agent_ids.append(agent_id)

        self.logger.info(f"已启动 {len(agent_ids)} 个测试 Subagents")

        # 等待所有 Subagents 完成
        timeout = self.config.get_execution_timeout()
        results = self.manager.wait_for_all_subagents(
            test_tasks[0]['skill_id'],
            test_tasks[0]['task_id'],
            timeout=timeout
        )

        # 收集结果
        for agent_id, result in results.items():
            if result is not None:
                self.test_results[agent_id] = result
            else:
                error = self.manager.get_subagent_error(agent_id)
                if error:
                    self.test_errors[agent_id] = error

        return self._generate_summary(results)

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成测试执行摘要

        Args:
            results: 所有测试任务的结果

        Returns:
            Dict[str, Any]: 测试摘要
        """
        summary = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'execution_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_agents': len(results),
            'successful_agents': sum(1 for r in results.values() if r is not None),
            'failed_agents': sum(1 for r in results.values() if r is None),
            'results': results
        }

        if summary['total_agents'] > 0:
            summary['success_rate'] = (
                summary['successful_agents'] / summary['total_agents'] * 100
            )

        self.logger.info(f"测试摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")

        return summary

    def stop(self):
        """停止并行测试执行器"""
        self.logger.info("停止并行测试执行器")
        self.manager.stop()


def create_unit_test_tasks(
    test_files: List[str],
    target_coverage: float = 0.8
) -> List[Dict[str, Any]]:
    """
    创建单元测试任务

    Args:
        test_files: 测试文件列表
        target_coverage: 目标覆盖率

    Returns:
        List[Dict[str, Any]]: 测试任务列表
    """
    tasks = []

    for i, test_file in enumerate(test_files):
        task = {
            'skill_id': 'go-sdk-ut',
            'task_id': f'unit-test-{i}',
            'metadata': {
                'test_file': test_file,
                'target_coverage': target_coverage
            },
            'context': {
                'test_file': test_file,
                'coverage_target': target_coverage
            },
            'execute_func': lambda ctx: execute_unit_test(ctx)
        }
        tasks.append(task)

    return tasks


def create_fuzz_test_tasks(
    targets: List[str],
    fuzz_duration: int = 30
) -> List[Dict[str, Any]]:
    """
    创建模糊测试任务

    Args:
        targets: 目标函数列表
        fuzz_duration: 模糊测试时长（秒）

    Returns:
        List[Dict[str, Any]]: 测试任务列表
    """
    tasks = []

    for i, target in enumerate(targets):
        task = {
            'skill_id': 'go-sdk-fuzz',
            'task_id': f'fuzz-test-{i}',
            'metadata': {
                'target_function': target,
                'duration': fuzz_duration
            },
            'context': {
                'target': target,
                'duration': fuzz_duration
            },
            'execute_func': lambda ctx: execute_fuzz_test(ctx)
        }
        tasks.append(task)

    return tasks


def create_perf_test_tasks(
    test_types: List[str],
    concurrency_levels: List[int] = None,
    file_sizes: List[str] = None
) -> List[Dict[str, Any]]:
    """
    创建性能测试任务

    Args:
        test_types: 测试类型列表（如 light, deep）
        concurrency_levels: 并发级别列表
        file_sizes: 文件大小列表

    Returns:
        List[Dict[str, Any]]: 测试任务列表
    """
    tasks = []
    concurrency_levels = concurrency_levels or [10, 50, 100]
    file_sizes = file_sizes or ['1MB', '10MB', '100MB']

    for i, (test_type, concurrency, file_size) in enumerate(
        zip(test_types, concurrency_levels, file_sizes)
    ):
        task = {
            'skill_id': 'go-sdk-perf',
            'task_id': f'perf-test-{i}',
            'metadata': {
                'test_type': test_type,
                'concurrency': concurrency,
                'file_size': file_size
            },
            'context': {
                'type': test_type,
                'concurrency': concurrency,
                'file_size': file_size
            },
            'execute_func': lambda ctx: execute_perf_test(ctx)
        }
        tasks.append(task)

    return tasks


def create_integration_test_tasks(
    modules: List[str]
) -> List[Dict[str, Any]]:
    """
    创建集成测试任务

    Args:
        modules: 测试模块列表

    Returns:
        List[Dict[str, Any]]: 测试任务列表
    """
    tasks = []

    for i, module in enumerate(modules):
        task = {
            'skill_id': 'go-sdk-integration',
            'task_id': f'integration-test-{i}',
            'metadata': {
                'module': module
            },
            'context': {
                'module': module
            },
            'execute_func': lambda ctx: execute_integration_test(ctx)
        }
        tasks.append(task)

    return tasks


# 模拟测试执行函数
def execute_unit_test(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行单元测试（模拟）

    Args:
        context: 执行上下文

    Returns:
        Dict[str, Any]: 测试结果
    """
    logger = get_logger("UnitTestExecutor")
    test_file = context.get('test_file', 'unknown')

    logger.info(f"开始执行单元测试: {test_file}")

    # 模拟测试执行
    time.sleep(2)  # 模拟耗时

    # 模拟结果
    result = {
        'test_file': test_file,
        'tests_run': 42,
        'tests_passed': 40,
        'tests_failed': 2,
        'coverage': 0.82,
        'execution_time': 2.0,
        'status': 'partial_failure'
    }

    logger.info(f"单元测试完成: {test_file} (passed: {result['tests_passed']}/{result['tests_run']})")

    return result


def execute_fuzz_test(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行模糊测试（模拟）

    Args:
        context: 执行上下文

    Returns:
        Dict[str, Any]: 测试结果
    """
    logger = get_logger("FuzzTestExecutor")
    target = context.get('target', 'unknown')
    duration = context.get('duration', 30)

    logger.info(f"开始模糊测试: {target} (duration: {duration}s)")

    # 模拟模糊测试执行
    time.sleep(min(duration, 3))  # 模拟耗时

    # 模拟结果
    result = {
        'target_function': target,
        'executions': 100000,
        'crashes_found': 1,
        'unique_crashes': 1,
        'coverage': 95.2,
        'execution_time': duration,
        'status': 'completed'
    }

    logger.info(f"模糊测试完成: {target} (crashes: {result['crashes_found']})")

    return result


def execute_perf_test(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行性能测试（模拟）

    Args:
        context: 执行上下文

    Returns:
        Dict[str, Any]: 测试结果
    """
    logger = get_logger("PerfTestExecutor")
    test_type = context.get('type', 'light')
    concurrency = context.get('concurrency', 10)
    file_size = context.get('file_size', '1MB')

    logger.info(f"开始性能测试: {test_type} (concurrency: {concurrency}, size: {file_size})")

    # 模拟性能测试执行
    time.sleep(2)  # 模拟耗时

    # 模拟结果
    result = {
        'test_type': test_type,
        'concurrency': concurrency,
        'file_size': file_size,
        'throughput_mb_s': 175.5,
        'ns_per_op': 5842341,
        'allocs_per_op': 28,
        'execution_time': 2.0,
        'status': 'completed'
    }

    logger.info(f"性能测试完成: {test_type} (throughput: {result['throughput_mb_s']} MB/s)")

    return result


def execute_integration_test(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行集成测试（模拟）

    Args:
        context: 执行上下文

    Returns:
        Dict[str, Any]: 测试结果
    """
    logger = get_logger("IntegrationTestExecutor")
    module = context.get('module', 'unknown')

    logger.info(f"开始集成测试: {module}")

    # 模拟集成测试执行
    time.sleep(3)  # 模拟耗时

    # 模拟结果
    result = {
        'module': module,
        'tests_total': 10,
        'tests_passed': 9,
        'tests_failed': 1,
        'tests_skipped': 0,
        'execution_time': 3.0,
        'cleanup_time': 1.0,
        'status': 'partial_failure'
    }

    logger.info(f"集成测试完成: {module} (passed: {result['tests_passed']}/{result['tests_total']})")

    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='并行测试执行器')
    parser.add_argument('--test-type', required=True,
                       choices=['unit', 'fuzz', 'perf', 'integration'],
                       help='测试类型')
    parser.add_argument('--workers', type=int, default=None,
                       help='并行工作数（默认：配置值）')
    parser.add_argument('--output', type=str, default='test-results.json',
                       help='输出文件路径')
    parser.add_argument('--config', type=str, default=None,
                       help='配置文件路径')

    # 测试类型特定参数
    parser.add_argument('--files', type=str, default=None,
                       help='测试文件列表（单元测试）')
    parser.add_argument('--targets', type=str, default=None,
                       help='目标函数列表（模糊测试）')
    parser.add_argument('--modules', type=str, default=None,
                       help='测试模块列表（集成测试）')
    parser.add_argument('--coverage', type=float, default=0.8,
                       help='目标覆盖率（单元测试）')
    parser.add_argument('--duration', type=int, default=30,
                       help='测试时长（秒，模糊测试）')

    args = parser.parse_args()

    # 加载配置
    config = Config()
    if args.config and Path(args.config).exists():
        config.load(Path(args.config))

    # 启用 Subagent
    config.set('subagent.enabled', True)
    if args.workers:
        config.set('subagent.parallel_workers', args.workers)

    # 创建执行器
    executor = ParallelTestExecutor(config)

    try:
        # 根据测试类型创建任务
        if args.test_type == 'unit':
            test_files = args.files.split(',') if args.files else ['client_test.go', 'util_test.go']
            tasks = create_unit_test_tasks(test_files, args.coverage)

        elif args.test_type == 'fuzz':
            targets = args.targets.split(',') if args.targets else ['xml', 'url', 'auth']
            tasks = create_fuzz_test_tasks(targets, args.duration)

        elif args.test_type == 'perf':
            test_types = ['light', 'deep']
            tasks = create_perf_test_tasks(test_types)

        elif args.test_type == 'integration':
            modules = args.modules.split(',') if args.modules else ['auth', 'bucket', 'object']
            tasks = create_integration_test_tasks(modules)

        # 执行测试
        summary = executor.execute_tests_parallel(tasks, args.workers)

        # 保存结果
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n测试摘要已保存到: {output_path}")
        print(f"成功率: {summary.get('success_rate', 0):.1f}%")
        print(f"成功: {summary['successful_agents']}/{summary['total_agents']}")

        # 返回状态码
        return 0 if summary['failed_agents'] == 0 else 1

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    finally:
        executor.stop()


if __name__ == '__main__':
    sys.exit(main())
