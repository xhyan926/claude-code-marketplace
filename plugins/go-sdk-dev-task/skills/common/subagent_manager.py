"""
Subagent 管理模块

提供 Subagent 的生命周期管理、消息路由和状态同步功能。
基于现有的 skill_base.py、error_handler.py、config.py 和 message_protocol.py 实现。
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass
import uuid

from .skill_base import SkillBase
from .error_handler import (
    SubagentErrorHandler,
    SubagentTimeoutError,
    SubagentExecutionError,
    SubagentCommunicationError
)
from .config import Config
from .message_protocol import (
    SubagentMessage,
    MessageType,
    SubagentState,
    MessageRouter,
    MessageQueue
)
from .logger import get_logger


@dataclass
class SubagentInfo:
    """
    Subagent 信息

    Attributes:
        agent_id: Subagent 唯一标识
        skill_id: 技能标识
        task_id: 任务标识
        session_id: 会话标识
        state: 当前状态
        start_time: 启动时间
        end_time: 结束时间
        progress: 进度（0.0-1.0）
        metadata: 附加元数据
    """
    agent_id: str
    skill_id: str
    task_id: str
    session_id: str
    state: SubagentState
    start_time: datetime
    end_time: Optional[datetime]
    progress: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'agent_id': self.agent_id,
            'skill_id': self.skill_id,
            'task_id': self.task_id,
            'session_id': self.session_id,
            'state': self.state.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'progress': self.progress,
            'metadata': self.metadata
        }


class SubagentManager:
    """
    Subagent 管理器

    负责管理 Subagent 的生命周期、消息路由和状态同步。
    """

    def __init__(self, config: Optional[Config] = None, session_id: Optional[str] = None):
        """
        初始化 Subagent Manager

        Args:
            config: 配置对象，如果为 None 则使用默认配置
            session_id: 会话标识，如果为 None 则自动生成
        """
        self.config = config or Config()
        self.session_id = session_id or str(uuid.uuid4())

        # 初始化组件
        self.logger = get_logger("SubagentManager")
        self.error_handler = SubagentErrorHandler(log_errors=True)
        self.message_router = MessageRouter()

        # Subagent 状态管理
        self.subagents: Dict[str, SubagentInfo] = {}  # key: agent_id
        self.task_agents: Dict[str, List[str]] = {}  # key: skill_id:task_id, value: list of agent_ids

        # 线程和事件循环
        self._event_loop = None
        self._worker_thread = None
        self._running = False
        self._heartbeat_interval = self.config.get_heartbeat_interval()

        # 回调函数
        self._on_message_callbacks: Dict[str, List[Callable]] = {}  # key: message_type

        # 结果存储
        self._results: Dict[str, Any] = {}  # key: agent_id
        self._errors: Dict[str, Exception] = {}  # key: agent_id

        # 锁
        self._lock = threading.Lock()

    def start(self):
        """启动 Subagent Manager"""
        if self._running:
            self.logger.warning("Subagent Manager 已经在运行")
            return

        self._running = True
        self._start_event_loop()
        self._start_message_processor()

        self.logger.info(f"Subagent Manager 已启动 (session: {self.session_id})")

    def stop(self):
        """停止 Subagent Manager"""
        if not self._running:
            return

        self._running = False

        # 停止所有 subagents
        with self._lock:
            for agent_id in list(self.subagents.keys()):
                self.stop_subagent(agent_id, reason="Manager shutting down")

        # 关闭消息路由器
        self.message_router.close()

        # 停止事件循环
        if self._event_loop and self._event_loop.is_running():
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)

        # 等待工作线程结束
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

        self.logger.info("Subagent Manager 已停止")

    def create_subagent(
        self,
        skill_id: str,
        task_id: str,
        run_in_background: bool = False,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建一个新的 Subagent

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            run_in_background: 是否在后台运行
            agent_id: Subagent 标识，如果为 None 则自动生成
            metadata: 附加元数据

        Returns:
            str: Subagent ID
        """
        agent_id = agent_id or f"{skill_id}:{task_id}:{uuid.uuid4().hex[:8]}"

        with self._lock:
            # 检查是否已存在
            if agent_id in self.subagents:
                self.logger.warning(f"Subagent {agent_id} 已存在")
                return agent_id

            # 创建消息队列
            queue = self.message_router.register_queue(skill_id, task_id)

            # 创建 Subagent 信息
            subagent_info = SubagentInfo(
                agent_id=agent_id,
                skill_id=skill_id,
                task_id=task_id,
                session_id=self.session_id,
                state=SubagentState.PENDING,
                start_time=datetime.now(),
                end_time=None,
                progress=0.0,
                metadata=metadata or {}
            )

            self.subagents[agent_id] = subagent_info

            # 注册到任务列表
            key = f"{skill_id}:{task_id}"
            if key not in self.task_agents:
                self.task_agents[key] = []
            self.task_agents[key].append(agent_id)

        self.logger.info(f"Subagent {agent_id} 已创建 (background={run_in_background})")
        return agent_id

    def start_subagent(
        self,
        agent_id: str,
        execute_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        启动 Subagent

        Args:
            agent_id: Subagent ID
            execute_func: 执行函数
            context: 执行上下文

        Returns:
            bool: 如果成功启动则返回 True，否则返回 False
        """
        with self._lock:
            subagent_info = self.subagents.get(agent_id)
            if not subagent_info:
                self.logger.error(f"Subagent {agent_id} 不存在")
                return False

            if subagent_info.state != SubagentState.PENDING:
                self.logger.warning(f"Subagent {agent_id} 状态不是 PENDING: {subagent_info.state.value}")
                return False

            # 更新状态
            subagent_info.state = SubagentState.RUNNING

        # 发送启动消息
        start_message = SubagentMessage.create_status_message(
            skill_id=subagent_info.skill_id,
            task_id=subagent_info.task_id,
            status=SubagentState.RUNNING,
            session_id=self.session_id,
            metadata=subagent_info.metadata
        )
        self.message_router.send(start_message)

        # 在线程中执行
        def run_subagent():
            try:
                result = execute_func(context or {})

                # 保存结果
                with self._lock:
                    self._results[agent_id] = result
                    subagent_info.progress = 1.0
                    subagent_info.state = SubagentState.COMPLETED
                    subagent_info.end_time = datetime.now()

                # 发送完成消息
                result_message = SubagentMessage.create_result_message(
                    skill_id=subagent_info.skill_id,
                    task_id=subagent_info.task_id,
                    result=result,
                    success=True,
                    session_id=self.session_id
                )
                self.message_router.send(result_message)

                self.logger.info(f"Subagent {agent_id} 执行成功")

            except Exception as e:
                # 保存错误
                with self._lock:
                    self._errors[agent_id] = e
                    subagent_info.state = SubagentState.FAILED
                    subagent_info.end_time = datetime.now()

                # 发送错误消息
                error_message = SubagentMessage.create_error_message(
                    skill_id=subagent_info.skill_id,
                    task_id=subagent_info.task_id,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    session_id=self.session_id
                )
                self.message_router.send(error_message)

                self.logger.error(f"Subagent {agent_id} 执行失败: {e}")

        thread = threading.Thread(target=run_subagent, daemon=True)
        thread.start()

        self.logger.info(f"Subagent {agent_id} 已启动")
        return True

    def stop_subagent(self, agent_id: str, reason: str = "") -> bool:
        """
        停止 Subagent

        Args:
            agent_id: Subagent ID
            reason: 停止原因

        Returns:
            bool: 如果成功停止则返回 True，否则返回 False
        """
        with self._lock:
            subagent_info = self.subagents.get(agent_id)
            if not subagent_info:
                return False

            if subagent_info.state in [SubagentState.COMPLETED, SubagentState.FAILED]:
                # 已经结束，不需要停止
                return True

            subagent_info.state = SubagentState.CANCELLED
            subagent_info.end_time = datetime.now()

            # 发送取消消息
            cancel_message = SubagentMessage.create_status_message(
                skill_id=subagent_info.skill_id,
                task_id=subagent_info.task_id,
                status=SubagentState.CANCELLED,
                session_id=self.session_id,
                metadata={'reason': reason}
            )
            self.message_router.send(cancel_message)

        self.logger.info(f"Subagent {agent_id} 已停止 (reason: {reason})")
        return True

    def get_subagent_info(self, agent_id: str) -> Optional[SubagentInfo]:
        """
        获取 Subagent 信息

        Args:
            agent_id: Subagent ID

        Returns:
            SubagentInfo: Subagent 信息，如果不存在则返回 None
        """
        with self._lock:
            return self.subagents.get(agent_id)

    def get_subagent_state(self, agent_id: str) -> Optional[SubagentState]:
        """
        获取 Subagent 状态

        Args:
            agent_id: Subagent ID

        Returns:
            SubagentState: Subagent 状态，如果不存在则返回 None
        """
        with self._lock:
            subagent_info = self.subagents.get(agent_id)
            return subagent_info.state if subagent_info else None

    def get_subagent_result(self, agent_id: str) -> Optional[Any]:
        """
        获取 Subagent 执行结果

        Args:
            agent_id: Subagent ID

        Returns:
            Any: 执行结果，如果未完成则返回 None
        """
        with self._lock:
            return self._results.get(agent_id)

    def get_subagent_error(self, agent_id: str) -> Optional[Exception]:
        """
        获取 Subagent 执行错误

        Args:
            agent_id: Subagent ID

        Returns:
            Exception: 执行错误，如果没有错误则返回 None
        """
        with self._lock:
            return self._errors.get(agent_id)

    def wait_for_subagent(
        self,
        agent_id: str,
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        等待 Subagent 完成

        Args:
            agent_id: Subagent ID
            timeout: 超时时间（秒）

        Returns:
            Dict[str, Any]: 执行结果，如果超时或失败则返回 None

        Raises:
            SubagentTimeoutError: 如果超时
        """
        start_time = time.time()
        timeout = timeout or self.config.get_execution_timeout()

        while True:
            subagent_info = self.get_subagent_info(agent_id)
            if not subagent_info:
                return None

            state = subagent_info.state
            if state == SubagentState.COMPLETED:
                return self.get_subagent_result(agent_id)
            elif state in [SubagentState.FAILED, SubagentState.CANCELLED]:
                return None

            if time.time() - start_time > timeout:
                self.stop_subagent(agent_id, reason="Timeout")
                raise SubagentTimeoutError(
                    f"Subagent {agent_id} 执行超时 ({timeout}秒)",
                    subagent_id=agent_id,
                    timeout=timeout
                )

            time.sleep(0.1)

    def wait_for_all_subagents(
        self,
        skill_id: str,
        task_id: str,
        timeout: Optional[float] = None
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        等待任务的所有 Subagents 完成

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            timeout: 超时时间（秒）

        Returns:
            Dict[str, Optional[Dict[str, Any]]]: 所有 Subagents 的执行结果
        """
        key = f"{skill_id}:{task_id}"
        agent_ids = self.task_agents.get(key, [])

        results = {}
        for agent_id in agent_ids:
            try:
                results[agent_id] = self.wait_for_subagent(agent_id, timeout)
            except SubagentTimeoutError as e:
                self.logger.error(f"等待 Subagent {agent_id} 超时: {e}")
                results[agent_id] = None

        return results

    def register_message_callback(
        self,
        message_type: MessageType,
        callback: Callable[[SubagentMessage], None]
    ):
        """
        注册消息回调函数

        Args:
            message_type: 消息类型
            callback: 回调函数
        """
        type_str = message_type.value
        if type_str not in self._on_message_callbacks:
            self._on_message_callbacks[type_str] = []
        self._on_message_callbacks[type_str].append(callback)

    def send_message(self, message: SubagentMessage, target_agent_id: Optional[str] = None) -> bool:
        """
        发送消息

        Args:
            message: 消息对象
            target_agent_id: 目标 Subagent ID，如果为 None 则根据 skill_id:task_id 路由

        Returns:
            bool: 是否发送成功
        """
        if target_agent_id:
            target_queue = self.message_router.get_queue(
                message.skill_id, message.task_id
            )
            return self.message_router.send(message, target_queue)
        else:
            return self.message_router.send(message)

    def get_all_subagent_info(self) -> List[Dict[str, Any]]:
        """
        获取所有 Subagents 的信息

        Returns:
            List[Dict[str, Any]]: 所有 Subagents 的信息
        """
        with self._lock:
            return [info.to_dict() for info in self.subagents.values()]

    def get_task_status(self, skill_id: str, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            skill_id: 技能标识
            task_id: 任务标识

        Returns:
            Dict[str, Any]: 任务状态
        """
        key = f"{skill_id}:{task_id}"
        agent_ids = self.task_agents.get(key, [])

        with self._lock:
            subagents_info = [
                self.subagents[agent_id].to_dict()
                for agent_id in agent_ids
                if agent_id in self.subagents
            ]

        # 计算总体状态
        total_agents = len(subagents_info)
        completed = sum(1 for info in subagents_info if info['state'] == SubagentState.COMPLETED.value)
        failed = sum(1 for info in subagents_info if info['state'] == SubagentState.FAILED.value)
        running = sum(1 for info in subagents_info if info['state'] == SubagentState.RUNNING.value)

        overall_state = SubagentState.COMPLETED.value if completed == total_agents else (
            SubagentState.FAILED.value if failed > 0 else (
                SubagentState.RUNNING.value if running > 0 else SubagentState.PENDING.value
            )
        )

        return {
            'skill_id': skill_id,
            'task_id': task_id,
            'overall_state': overall_state,
            'total_agents': total_agents,
            'completed': completed,
            'failed': failed,
            'running': running,
            'subagents': subagents_info
        }

    def _start_event_loop(self):
        """启动事件循环"""
        if self._event_loop is None:
            self._event_loop = asyncio.new_event_loop()

        if not self._event_loop.is_running():
            def run_loop():
                asyncio.set_event_loop(self._event_loop)
                self._event_loop.run_forever()

            self._worker_thread = threading.Thread(target=run_loop, daemon=True)
            self._worker_thread.start()

    def _start_message_processor(self):
        """启动消息处理器"""
        def process_messages():
            while self._running:
                try:
                    # 从全局队列接收消息
                    message = self.message_router.receive_global(block=False)
                    if message:
                        self._process_message(message)
                except Exception as e:
                    self.logger.error(f"处理消息时出错: {e}")

                time.sleep(0.1)

        processor_thread = threading.Thread(target=process_messages, daemon=True)
        processor_thread.start()

    def _process_message(self, message: SubagentMessage):
        """
        处理消息

        Args:
            message: 消息对象
        """
        # 更新 Subagent 状态
        if message.message_type == MessageType.STATUS:
            with self._lock:
                # 查找对应的 subagent
                for subagent_info in self.subagents.values():
                    if (subagent_info.skill_id == message.skill_id and
                        subagent_info.task_id == message.task_id):
                        # 更新状态
                        if 'status' in message.payload:
                            try:
                                subagent_info.state = SubagentState(message.payload['status'])
                            except ValueError:
                                pass
                        if 'progress' in message.payload:
                            subagent_info.progress = message.payload['progress']
                        break

        # 调用回调函数
        callbacks = self._on_message_callbacks.get(message.message_type.value, [])
        for callback in callbacks:
            try:
                callback(message)
            except Exception as e:
                self.logger.error(f"消息回调出错: {e}")


class SubagentManagerFactory:
    """
    Subagent Manager 工厂

    用于创建和配置 Subagent Manager 实例。
    """

    @staticmethod
    def create_manager(config: Optional[Config] = None) -> SubagentManager:
        """
        创建 Subagent Manager

        Args:
            config: 配置对象

        Returns:
            SubagentManager: Subagent Manager 实例
        """
        return SubagentManager(config=config)

    @staticmethod
    def create_for_skill(
        skill: SkillBase,
        session_id: Optional[str] = None
    ) -> SubagentManager:
        """
        为特定技能创建 Subagent Manager

        Args:
            skill: 技能对象
            session_id: 会话标识

        Returns:
            SubagentManager: Subagent Manager 实例
        """
        return SubagentManager(
            config=skill.config,
            session_id=session_id
        )
