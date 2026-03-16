"""
文档流水线管理器

使用 Subagent Manager 实现文档生成和验证的并行执行，构建文档生成流水线。
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


class DocPipelineManager:
    """
    文档流水线管理器

    管理文档生成和验证的并行执行，构建完整的文档生成流水线。
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化文档流水线管理器

        Args:
            config: 配置对象，如果为 None 则使用默认配置
        """
        self.config = config or Config()
        self.logger = get_logger("DocPipelineManager")

        # 创建 Subagent Manager
        self.manager = SubagentManagerFactory.create_manager(self.config)
        self.manager.start()

        # 文档结果
        self.doc_results: Dict[str, Any] = {}
        self.verification_results: Dict[str, Any] = {}

        # 注册消息回调
        self._register_message_callbacks()

    def _register_message_callbacks(self):
        """注册消息回调"""
        def on_status(message: SubagentMessage):
            self.logger.info(
                f"文档进度: {message.skill_id}:{message.task_id} = "
                f"{message.payload.get('status', 'unknown')} "
                f"({message.payload.get('progress', 0)*100:.1f}%)"
            )

        def on_result(message: SubagentMessage):
            self.logger.info(
                f"文档结果: {message.skill_id}:{message.task_id} = "
                f"{message.payload.get('success', False)}"
            )

        def on_error(message: SubagentMessage):
            self.logger.error(
                f"文档错误: {message.skill_id}:{message.task_id} = "
                f"{message.payload.get('error_message', 'Unknown error')}"
            )

        self.manager.register_message_callback(MessageType.STATUS, on_status)
        self.manager.register_message_callback(MessageType.RESULT, on_result)
        self.manager.register_message_callback(MessageType.ERROR, on_error)

    def execute_pipeline(
        self,
        doc_tasks: List[Dict[str, Any]],
        verification_tasks: List[Dict[str, Any]],
        parallel_workers: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行文档生成流水线

        Args:
            doc_tasks: 文档生成任务列表
            verification_tasks: 文档验证任务列表
            parallel_workers: 并行工作数，如果为 None 则使用配置值

        Returns:
            Dict[str, Any]: 流水线执行结果
        """
        # 获取并行工作数
        parallel_workers = parallel_workers or self.config.get_parallel_workers()

        self.logger.info(f"启动文档流水线 (workers: {parallel_workers})")

        # 创建并启动文档生成任务
        doc_agent_ids = []
        for task in doc_tasks:
            agent_id = self.manager.create_subagent(
                skill_id=task['skill_id'],
                task_id=task['task_id'],
                metadata=task.get('metadata', {})
            )

            # 启动文档生成 Subagent
            self.manager.start_subagent(
                agent_id,
                task['execute_func'],
                context=task.get('context', {})
            )

            doc_agent_ids.append(agent_id)

        self.logger.info(f"已启动 {len(doc_agent_ids)} 个文档生成 Subagents")

        # 等待所有文档生成完成
        timeout = self.config.get_execution_timeout()
        doc_results = self.manager.wait_for_all_subagents(
            doc_tasks[0]['skill_id'],
            doc_tasks[0]['task_id'],
            timeout=timeout
        )

        # 收集文档生成结果
        for agent_id, result in doc_results.items():
            if result is not None:
                self.doc_results[agent_id] = result

        # 验证文档生成结果
        successful_docs = [
            agent_id for agent_id, result in doc_results.items()
            if result is not None and result.get('success', False)
        ]

        if not successful_docs:
            self.logger.error("没有成功生成的文档，跳过验证阶段")
            return self._generate_pipeline_summary(doc_results, {})

        # 创建并启动文档验证任务
        verif_agent_ids = []
        for i, task in enumerate(verification_tasks):
            # 为每个验证任务分配对应的文档生成结果
            corresponding_doc_agent = successful_docs[i % len(successful_docs)]
            doc_result = doc_results[corresponding_doc_agent]

            agent_id = self.manager.create_subagent(
                skill_id=task['skill_id'],
                task_id=task['task_id'],
                metadata={
                    **task.get('metadata', {}),
                    'generated_doc': doc_result
                }
            )

            # 启动文档验证 Subagent
            self.manager.start_subagent(
                agent_id,
                task['execute_func'],
                context={
                    **task.get('context', {}),
                    'generated_doc': doc_result
                }
            )

            verif_agent_ids.append(agent_id)

        self.logger.info(f"已启动 {len(verif_agent_ids)} 个文档验证 Subagents")

        # 等待所有文档验证完成
        verif_results = self.manager.wait_for_all_subagents(
            verification_tasks[0]['skill_id'],
            verification_tasks[0]['task_id'],
            timeout=timeout
        )

        # 收集文档验证结果
        for agent_id, result in verif_results.items():
            if result is not None:
                self.verification_results[agent_id] = result

        # 生成流水线摘要
        return self._generate_pipeline_summary(doc_results, verif_results)

    def _generate_pipeline_summary(
        self,
        doc_results: Dict[str, Any],
        verif_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成流水线摘要

        Args:
            doc_results: 文档生成结果
            verif_results: 文档验证结果

        Returns:
            Dict[str, Any]: 流水线摘要
        """
        summary = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'execution_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'doc_generation': {
                'total_tasks': len(doc_results),
                'successful_tasks': sum(1 for r in doc_results.values() if r and r.get('success', False)),
                'failed_tasks': sum(1 for r in doc_results.values() if r is None or not r.get('success', False)),
                'results': doc_results
            },
            'doc_verification': {
                'total_tasks': len(verif_results),
                'successful_tasks': sum(1 for r in verif_results.values() if r and r.get('success', False)),
                'failed_tasks': sum(1 for r in verif_results.values() if r is None or not r.get('success', False)),
                'results': verif_results
            }
        }

        # 计算整体状态
        doc_success_rate = (
            summary['doc_generation']['successful_tasks'] / summary['doc_generation']['total_tasks']
            if summary['doc_generation']['total_tasks'] > 0 else 1.0
        )

        verif_success_rate = (
            summary['doc_verification']['successful_tasks'] / summary['doc_verification']['total_tasks']
            if summary['doc_verification']['total_tasks'] > 0 else 1.0
        )

        summary['overall_status'] = {
            'doc_generation_success_rate': doc_success_rate * 100,
            'doc_verification_success_rate': verif_success_rate * 100,
            'overall_success_rate': (doc_success_rate * verif_success_rate) * 100,
            'status': 'passed' if doc_success_rate == 1.0 and verif_success_rate == 1.0 else 'partial_failure'
        }

        self.logger.info(f"流水线摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")

        return summary

    def stop(self):
        """停止文档流水线管理器"""
        self.logger.info("停止文档流水线管理器")
        self.manager.stop()


def create_doc_generation_tasks(
    api_modules: List[str],
    output_dir: str = './docs'
) -> List[Dict[str, Any]]:
    """
    创建文档生成任务

    Args:
        api_modules: API 模块列表
        output_dir: 输出目录

    Returns:
        List[Dict[str, Any]]: 文档生成任务列表
    """
    tasks = []

    for i, module in enumerate(api_modules):
        task = {
            'skill_id': 'sdk-doc',
            'task_id': f'doc-generation-{i}',
            'metadata': {
                'api_module': module,
                'output_dir': output_dir,
                'include_examples': True
            },
            'context': {
                'module': module,
                'output_dir': output_dir,
                'include_examples': True
            },
            'execute_func': lambda ctx: generate_api_doc(ctx)
        }
        tasks.append(task)

    return tasks


def create_doc_verification_tasks(
    doc_results: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    创建文档验证任务

    Args:
        doc_results: 文档生成结果

    Returns:
        List[Dict[str, Any]]: 文档验证任务列表
    """
    tasks = []

    for i, (agent_id, doc_result) in enumerate(doc_results.items()):
        if doc_result and doc_result.get('success', False):
            task = {
                'skill_id': 'doc-verifier',
                'task_id': f'doc-verification-{i}',
                'metadata': {
                    'doc_file': doc_result.get('output_file', ''),
                    'api_module': doc_result.get('api_module', ''),
                    'generated_doc': doc_result
                },
                'context': {
                    'doc_file': doc_result.get('output_file', ''),
                    'api_module': doc_result.get('api_module', ''),
                    'generated_doc': doc_result
                },
                'execute_func': lambda ctx: verify_api_doc(ctx)
            }
            tasks.append(task)

    return tasks


# 模拟文档生成和验证函数
def generate_api_doc(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成 API 文档（模拟）

    Args:
        context: 执行上下文

    Returns:
        Dict[str, Any]: 文档生成结果
    """
    logger = get_logger("DocGenerator")
    module = context.get('module', 'unknown')
    output_dir = context.get('output_dir', './docs')

    logger.info(f"开始生成 API 文档: {module}")

    # 模拟文档生成
    time.sleep(3)  # 模拟耗时

    # 模拟结果
    doc_file = f'{module}/API.md'
    result = {
        'api_module': module,
        'output_file': doc_file,
        'output_path': f'{output_dir}/{doc_file}',
        'apis_documented': 15,
        'examples_generated': 10,
        'tables_created': 5,
        'execution_time': 3.0,
        'success': True
    }

    logger.info(f"API 文档生成完成: {module} (APIs: {result['apis_documented']})")

    return result


def verify_api_doc(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证 API 文档（模拟）

    Args:
        context: 执行上下文

    Returns:
        Dict[str, Any]: 文档验证结果
    """
    logger = get_logger("DocVerifier")
    doc_file = context.get('doc_file', 'unknown')
    generated_doc = context.get('generated_doc', {})

    logger.info(f"开始验证 API 文档: {doc_file}")

    # 模拟文档验证
    time.sleep(2)  # 模拟耗时

    # 模拟结果
    result = {
        'doc_file': doc_file,
        'api_module': context.get('api_module', ''),
        'checks_total': 10,
        'checks_passed': 9,
        'checks_failed': 1,
        'issues_found': [
            {
                'type': 'missing_example',
                'severity': 'medium',
                'description': '部分 API 缺少示例代码'
            }
        ],
        'execution_time': 2.0,
        'success': True
    }

    logger.info(f"API 文档验证完成: {doc_file} (passed: {result['checks_passed']}/{result['checks_total']})")

    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文档流水线管理器')
    parser.add_argument('--modules', type=str, required=True,
                       help='API 模块列表（逗号分隔）')
    parser.add_argument('--output', type=str, default='./docs',
                       help='输出目录路径')
    parser.add_argument('--workers', type=int, default=None,
                       help='并行工作数（默认：配置值）')
    parser.add_argument('--config', type=str, default=None,
                       help='配置文件路径')
    parser.add_argument('--no-verification', action='store_true',
                       help='跳过文档验证阶段')

    args = parser.parse_args()

    # 加载配置
    config = Config()
    if args.config and Path(args.config).exists():
        config.load(Path(args.config))

    # 启用 Subagent
    config.set('subagent.enabled', True)
    if args.workers:
        config.set('subagent.parallel_workers', args.workers)

    # 创建流水线管理器
    pipeline = DocPipelineManager(config)

    try:
        # 解析 API 模块
        api_modules = [m.strip() for m in args.modules.split(',')]

        # 创建文档生成任务
        doc_tasks = create_doc_generation_tasks(api_modules, args.output)

        # 创建文档验证任务（如果需要）
        verif_tasks = []
        if not args.no_verification:
            # 先执行文档生成以获得结果
            # 注意：实际实现中应该分两步，这里简化处理
            verif_tasks = create_doc_verification_tasks({})

        # 执行流水线
        summary = pipeline.execute_pipeline(doc_tasks, verif_tasks, args.workers)

        # 保存结果
        output_path = Path(args.output) / 'pipeline-summary.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n流水线摘要已保存到: {output_path}")
        print(f"文档生成成功率: {summary['overall_status']['doc_generation_success_rate']:.1f}%")
        print(f"文档验证成功率: {summary['overall_status']['doc_verification_success_rate']:.1f}%")
        print(f"整体成功率: {summary['overall_status']['overall_success_rate']:.1f}%")

        # 返回状态码
        return 0 if summary['overall_status']['status'] == 'passed' else 1

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    finally:
        pipeline.stop()


if __name__ == '__main__':
    sys.exit(main())
