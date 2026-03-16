"""
Subagent 基础设施测试

测试新创建的 Subagent 相关模块的功能。
"""

import unittest
from unittest.mock import Mock, patch
import time

from skills.common import (
    SubagentManager,
    SubagentManagerFactory,
    Config
)
from skills.common.message_protocol import (
    SubagentMessage,
    MessageType,
    SubagentState,
    MessageQueue,
    MessageRouter
)
from skills.common.error_handler import (
    SubagentError,
    SubagentTimeoutError,
    SubagentExecutionError,
    SubagentErrorHandler
)


class TestSubagentMessage(unittest.TestCase):
    """测试 Subagent 消息协议"""

    def test_create_status_message(self):
        """测试创建状态消息"""
        message = SubagentMessage.create_status_message(
            skill_id="test-skill",
            task_id="test-task",
            status=SubagentState.RUNNING,
            progress=0.5,
            session_id="test-session"
        )

        self.assertEqual(message.skill_id, "test-skill")
        self.assertEqual(message.task_id, "test-task")
        self.assertEqual(message.message_type, MessageType.STATUS)
        self.assertEqual(message.payload['status'], SubagentState.RUNNING.value)
        self.assertEqual(message.payload['progress'], 0.5)

    def test_create_result_message(self):
        """测试创建结果消息"""
        result = {'status': 'success', 'data': [1, 2, 3]}
        message = SubagentMessage.create_result_message(
            skill_id="test-skill",
            task_id="test-task",
            result=result,
            success=True,
            session_id="test-session"
        )

        self.assertEqual(message.message_type, MessageType.RESULT)
        self.assertTrue(message.payload['success'])
        self.assertEqual(message.payload['result'], result)

    def test_create_error_message(self):
        """测试创建错误消息"""
        message = SubagentMessage.create_error_message(
            skill_id="test-skill",
            task_id="test-task",
            error_message="Test error",
            error_code=1001,
            error_type="TestError",
            session_id="test-session",
            suggestion="Try again"
        )

        self.assertEqual(message.message_type, MessageType.ERROR)
        self.assertEqual(message.payload['error_message'], "Test error")
        self.assertEqual(message.payload['error_code'], 1001)
        self.assertEqual(message.payload['suggestion'], "Try again")

    def test_message_serialization(self):
        """测试消息序列化和反序列化"""
        original_message = SubagentMessage.create_status_message(
            skill_id="test-skill",
            task_id="test-task",
            status=SubagentState.COMPLETED,
            progress=1.0,
            session_id="test-session"
        )

        # 序列化
        json_str = original_message.to_json()

        # 反序列化
        restored_message = SubagentMessage.from_json(json_str)

        self.assertEqual(restored_message.skill_id, original_message.skill_id)
        self.assertEqual(restored_message.task_id, original_message.task_id)
        self.assertEqual(restored_message.message_type, original_message.message_type)
        self.assertEqual(restored_message.payload, original_message.payload)


class TestMessageQueue(unittest.TestCase):
    """测试消息队列"""

    def test_put_and_get_message(self):
        """测试放入和获取消息"""
        queue = MessageQueue(max_size=10)

        message = SubagentMessage.create_status_message(
            skill_id="test-skill",
            task_id="test-task",
            status=SubagentState.RUNNING,
            session_id="test-session"
        )

        # 放入消息
        self.assertTrue(queue.put(message))

        # 获取消息
        retrieved_message = queue.get(block=False)
        self.assertIsNotNone(retrieved_message)
        self.assertEqual(retrieved_message.skill_id, "test-skill")

    def test_queue_empty_check(self):
        """测试队列空检查"""
        queue = MessageQueue()
        self.assertTrue(queue.empty())

        message = SubagentMessage.create_status_message(
            skill_id="test-skill",
            task_id="test-task",
            status=SubagentState.RUNNING,
            session_id="test-session"
        )
        queue.put(message)

        self.assertFalse(queue.empty())

    def test_queue_size(self):
        """测试队列大小"""
        queue = MessageQueue(max_size=5)

        for i in range(3):
            message = SubagentMessage.create_status_message(
                skill_id="test-skill",
                task_id="test-task",
                status=SubagentState.RUNNING,
                session_id=f"session-{i}"
            )
            queue.put(message)

        self.assertEqual(len(queue), 3)


class TestMessageRouter(unittest.TestCase):
    """测试消息路由器"""

    def test_register_and_unregister_queue(self):
        """测试注册和注销队列"""
        router = MessageRouter()

        queue = router.register_queue("test-skill", "test-task")
        self.assertIsNotNone(queue)

        router.unregister_queue("test-skill", "test-task")
        self.assertIsNone(router.get_queue("test-skill", "test-task"))

    def test_send_and_receive_message(self):
        """测试发送和接收消息"""
        router = MessageRouter()

        # 注册队列
        router.register_queue("test-skill", "test-task")

        # 发送消息
        message = SubagentMessage.create_status_message(
            skill_id="test-skill",
            task_id="test-task",
            status=SubagentState.RUNNING,
            session_id="test-session"
        )
        self.assertTrue(router.send(message))

        # 接收消息
        received = router.receive("test-skill", "test-task", block=False)
        self.assertIsNotNone(received)
        self.assertEqual(received.skill_id, "test-skill")


class TestSubagentManager(unittest.TestCase):
    """测试 Subagent Manager"""

    def setUp(self):
        """设置测试环境"""
        self.config = Config()
        self.config.set('subagent.enabled', True)
        self.manager = SubagentManager(config=self.config)
        self.manager.start()

    def tearDown(self):
        """清理测试环境"""
        self.manager.stop()

    def test_create_subagent(self):
        """测试创建 Subagent"""
        agent_id = self.manager.create_subagent(
            skill_id="test-skill",
            task_id="test-task"
        )

        self.assertIsNotNone(agent_id)
        info = self.manager.get_subagent_info(agent_id)
        self.assertIsNotNone(info)
        self.assertEqual(info.skill_id, "test-skill")
        self.assertEqual(info.task_id, "test-task")
        self.assertEqual(info.state, SubagentState.PENDING)

    def test_start_and_wait_subagent(self):
        """测试启动和等待 Subagent"""
        agent_id = self.manager.create_subagent(
            skill_id="test-skill",
            task_id="test-task"
        )

        def simple_execute(context: dict) -> dict:
            time.sleep(0.1)
            return {'result': 'success'}

        self.assertTrue(self.manager.start_subagent(agent_id, simple_execute))

        result = self.manager.wait_for_subagent(agent_id, timeout=5)
        self.assertIsNotNone(result)
        self.assertEqual(result['result'], 'success')

    def test_subagent_timeout(self):
        """测试 Subagent 超时"""
        agent_id = self.manager.create_subagent(
            skill_id="test-skill",
            task_id="test-task"
        )

        def slow_execute(context: dict) -> dict:
            time.sleep(5)
            return {'result': 'success'}

        self.assertTrue(self.manager.start_subagent(agent_id, slow_execute))

        with self.assertRaises(SubagentTimeoutError):
            self.manager.wait_for_subagent(agent_id, timeout=0.5)

    def test_parallel_subagents(self):
        """测试并行执行多个 Subagents"""
        agents = []

        for i in range(3):
            agent_id = self.manager.create_subagent(
                skill_id="test-skill",
                task_id=f"test-task-{i}"
            )
            agents.append(agent_id)

        def execute_with_delay(context: dict) -> dict:
            delay = context.get('delay', 0.1)
            time.sleep(delay)
            return {'delay': delay}

        # 并行启动
        for i, agent_id in enumerate(agents):
            self.manager.start_subagent(
                agent_id,
                lambda ctx, d=0.1: execute_with_delay({'delay': d})
            )

        # 等待所有完成
        results = self.manager.wait_for_all_subagents("test-skill", "test-task-0", timeout=10)

        self.assertEqual(len(results), 3)

    def test_get_task_status(self):
        """测试获取任务状态"""
        agent_id = self.manager.create_subagent(
            skill_id="test-skill",
            task_id="test-task"
        )

        status = self.manager.get_task_status("test-skill", "test-task")

        self.assertEqual(status['skill_id'], "test-skill")
        self.assertEqual(status['task_id'], "test-task")
        self.assertEqual(status['total_agents'], 1)
        self.assertEqual(status['overall_state'], SubagentState.PENDING.value)


class TestSubagentErrorHandler(unittest.TestCase):
    """测试 Subagent 错误处理"""

    def test_subagent_error_recovery(self):
        """测试 Subagent 错误恢复性"""
        error = SubagentError(
            "Test error",
            subagent_id="test-agent"
        )

        # 默认是可恢复的
        self.assertTrue(error.is_recoverable())

    def test_subagent_timeout_error_recovery(self):
        """测试超时错误恢复性"""
        error = SubagentTimeoutError(
            "Timeout error",
            subagent_id="test-agent",
            timeout=10.0
        )

        self.assertTrue(error.is_recoverable())

    def test_subagent_startup_error_recovery(self):
        """测试启动错误恢复性"""
        error = SubagentError.__new__(SubagentError)
        error.message = "Startup error"
        error.code = 6003
        error.subagent_id = "test-agent"
        error.suggestion = None

        # 启动错误通常不可恢复
        # 这里需要根据实际实现调整


class TestSubagentManagerFactory(unittest.TestCase):
    """测试 Subagent Manager 工厂"""

    def test_create_manager_with_config(self):
        """测试使用配置创建 Manager"""
        config = Config()
        config.set('subagent.enabled', True)

        manager = SubagentManagerFactory.create_manager(config=config)
        self.assertIsNotNone(manager)
        self.assertEqual(manager.config.is_subagent_enabled(), True)

    def test_create_manager_default_config(self):
        """测试使用默认配置创建 Manager"""
        manager = SubagentManagerFactory.create_manager()
        self.assertIsNotNone(manager)
        self.assertFalse(manager.config.is_subagent_enabled())


if __name__ == '__main__':
    unittest.main()
