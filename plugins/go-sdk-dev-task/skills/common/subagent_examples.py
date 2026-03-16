"""
Subagent 使用示例

展示如何使用新创建的 Subagent 基础设施。
"""

from .subagent_manager import SubagentManager, SubagentManagerFactory
from .config import Config
from .message_protocol import SubagentMessage, MessageType, SubagentState
from .logger import get_logger


def example_basic_usage():
    """基本使用示例"""
    logger = get_logger("SubagentExample")

    # 创建配置
    config = Config()
    config.set('subagent.enabled', True)
    config.set('subagent.parallel_workers', 2)

    # 创建 Subagent Manager
    manager = SubagentManagerFactory.create_manager(config)
    manager.start()

    try:
        # 创建一个 subagent
        agent_id = manager.create_subagent(
            skill_id="go-sdk-ut",
            task_id="write-unit-tests",
            metadata={
                'test_files': ['client_test.go', 'util_test.go'],
                'coverage_target': 0.8
            }
        )

        # 定义执行函数
        def execute_unit_tests(context: dict) -> dict:
            logger.info("开始执行单元测试...")
            # 模拟耗时操作
            import time
            time.sleep(2)
            return {
                'tests_run': 42,
                'tests_passed': 42,
                'coverage': 0.85,
                'duration': 2.0
            }

        # 启动 subagent
        manager.start_subagent(agent_id, execute_unit_tests)

        # 等待完成
        result = manager.wait_for_subagent(agent_id, timeout=30)
        logger.info(f"Subagent 执行结果: {result}")

        # 获取状态
        status = manager.get_task_status("go-sdk-ut", "write-unit-tests")
        logger.info(f"任务状态: {status}")

    finally:
        manager.stop()


def example_parallel_execution():
    """并行执行示例"""
    logger = get_logger("ParallelExample")

    # 创建配置
    config = Config()
    config.set('subagent.enabled', True)
    config.set('subagent.parallel_workers', 4)

    # 创建 Subagent Manager
    manager = SubagentManagerFactory.create_manager(config)
    manager.start()

    try:
        # 创建多个 subagents
        task_id = "full-testing"
        agents = []

        # 1. 单元测试
        agent_id1 = manager.create_subagent(
            skill_id="go-sdk-ut",
            task_id=task_id,
            metadata={'type': 'unit_tests'}
        )
        agents.append(('go-sdk-ut', agent_id1))

        # 2. 模糊测试
        agent_id2 = manager.create_subagent(
            skill_id="go-sdk-fuzz",
            task_id=task_id,
            metadata={'type': 'fuzz_tests'}
        )
        agents.append(('go-sdk-fuzz', agent_id2))

        # 3. 性能测试
        agent_id3 = manager.create_subagent(
            skill_id="go-sdk-perf",
            task_id=task_id,
            metadata={'type': 'perf_tests'}
        )
        agents.append(('go-sdk-perf', agent_id3))

        # 4. 集成测试
        agent_id4 = manager.create_subagent(
            skill_id="go-sdk-integration",
            task_id=task_id,
            metadata={'type': 'integration_tests'}
        )
        agents.append(('go-sdk-integration', agent_id4))

        # 定义不同的执行函数
        def execute_test(skill_id: str, context: dict) -> dict:
            logger.info(f"执行 {skill_id} 测试...")
            import time
            # 模拟不同耗时
            delay = {'go-sdk-ut': 2, 'go-sdk-fuzz': 3, 'go-sdk-perf': 4, 'go-sdk-integration': 5}
            time.sleep(delay.get(skill_id, 2))
            return {
                'skill': skill_id,
                'status': 'passed',
                'metrics': {'execution_time': delay.get(skill_id, 2)}
            }

        # 并行启动所有 subagents
        for skill_id, agent_id in agents:
            manager.start_subagent(
                agent_id,
                lambda ctx, sid=skill_id: execute_test(sid, ctx)
            )

        # 等待所有完成
        results = manager.wait_for_all_subagents("go-sdk-ut", task_id, timeout=30)
        logger.info(f"所有测试结果: {results}")

        # 获取任务状态
        status = manager.get_task_status("go-sdk-ut", task_id)
        logger.info(f"任务整体状态: {status}")

    finally:
        manager.stop()


def example_message_callbacks():
    """消息回调示例"""
    logger = get_logger("MessageCallbackExample")

    # 创建 Subagent Manager
    manager = SubagentManagerFactory.create_manager()
    manager.start()

    try:
        # 注册消息回调
        def on_status_message(message: SubagentMessage):
            logger.info(f"收到状态更新: {message.payload}")

        def on_result_message(message: SubagentMessage):
            logger.info(f"收到执行结果: {message.payload}")

        def on_error_message(message: SubagentMessage):
            logger.error(f"收到错误消息: {message.payload}")

        manager.register_message_callback(MessageType.STATUS, on_status_message)
        manager.register_message_callback(MessageType.RESULT, on_result_message)
        manager.register_message_callback(MessageType.ERROR, on_error_message)

        # 创建并启动 subagent
        agent_id = manager.create_subagent(
            skill_id="code-reviewer",
            task_id="review-auth-module"
        )

        def execute_review(context: dict) -> dict:
            logger.info("开始代码审查...")
            # 发送进度更新
            manager.send_message(
                SubagentMessage.create_status_message(
                    skill_id="code-reviewer",
                    task_id="review-auth-module",
                    status=SubagentState.RUNNING,
                    progress=0.5,
                    session_id=manager.session_id,
                    metadata={'current_file': 'auth.go'}
                )
            )

            import time
            time.sleep(2)
            return {
                'issues_found': 3,
                'suggestions': 5,
                'score': 85
            }

        manager.start_subagent(agent_id, execute_review)
        manager.wait_for_subagent(agent_id)

    finally:
        manager.stop()


def example_error_handling():
    """错误处理示例"""
    logger = get_logger("ErrorHandlingExample")

    # 创建 Subagent Manager
    manager = SubagentManagerFactory.create_manager()
    manager.start()

    try:
        agent_id = manager.create_subagent(
            skill_id="sdk-doc",
            task_id="generate-api-docs"
        )

        def execute_with_error(context: dict) -> dict:
            logger.info("开始生成文档...")
            # 模拟错误
            raise ValueError("API 文档数据不完整")

        manager.start_subagent(agent_id, execute_with_error)

        # 等待并处理错误
        try:
            result = manager.wait_for_subagent(agent_id, timeout=10)
            logger.info(f"执行结果: {result}")
        except Exception as e:
            logger.error(f"执行失败: {e}")

        # 获取错误信息
        error = manager.get_subagent_error(agent_id)
        if error:
            logger.error(f"Subagent 错误: {error}")

        # 获取最终状态
        state = manager.get_subagent_state(agent_id)
        logger.info(f"Subagent 状态: {state.value if state else 'Unknown'}")

    finally:
        manager.stop()


def example_skill_integration():
    """与现有技能集成的示例"""
    logger = get_logger("SkillIntegrationExample")

    # 这个示例展示如何在现有技能中使用 subagent
    # 假设有一个 go-sdk-dev-task 技能

    # 创建配置
    config = Config()
    config.set('subagent.enabled', True)

    # 创建 Manager
    manager = SubagentManagerFactory.create_manager(config)
    manager.start()

    try:
        # 在 go-sdk-dev-task 中创建多个 subagents
        # 用于并行生成子任务文档

        subtasks = [
            {'id': 'subtask-1', 'title': '实现客户端连接'},
            {'id': 'subtask-2', 'title': '实现对象上传'},
            {'id': 'subtask-3', 'title': '实现对象下载'},
        ]

        agent_ids = []

        # 为每个子任务创建一个 subagent
        for subtask in subtasks:
            agent_id = manager.create_subagent(
                skill_id="sdk-doc",
                task_id=subtask['id'],
                metadata={
                    'subtask_title': subtask['title'],
                    'api_methods': ['PutObject', 'GetObject']
                }
            )
            agent_ids.append(agent_id)

        # 为每个 subagent 定义执行函数
        def generate_subtask_docs(context: dict) -> dict:
            metadata = context.get('metadata', {})
            logger.info(f"为子任务 '{metadata.get('subtask_title')}' 生成文档...")
            import time
            time.sleep(1)
            return {
                'subtask_id': metadata.get('subtask_id'),
                'docs_generated': len(metadata.get('api_methods', [])),
                'output_file': f"{metadata.get('subtask_id')}_API.md"
            }

        # 并行启动所有 subagents
        for agent_id in agent_ids:
            manager.start_subagent(agent_id, generate_subtask_docs)

        # 等待所有完成
        results = {}
        for agent_id in agent_ids:
            try:
                result = manager.wait_for_subagent(agent_id, timeout=30)
                results[agent_id] = result
            except Exception as e:
                logger.error(f"Subagent {agent_id} 执行失败: {e}")
                results[agent_id] = None

        logger.info(f"所有子任务文档生成完成: {results}")

    finally:
        manager.stop()


if __name__ == "__main__":
    # 运行示例
    import sys

    examples = {
        'basic': example_basic_usage,
        'parallel': example_parallel_execution,
        'callbacks': example_message_callbacks,
        'error': example_error_handling,
        'integration': example_skill_integration
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("可用的示例:")
        for name in examples.keys():
            print(f"  {name}")
        print("\n用法: python subagent_examples.py <example_name>")
