"""
消息传递协议模块

定义 Subagent 之间的消息传递协议和数据结构。
基于现有的 error_handler.py 和 error_codes.json 实现。
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from .error_handler import SkillError


class MessageType(Enum):
    """消息类型枚举"""
    STATUS = "status"        # 状态更新消息
    RESULT = "result"        # 执行结果消息
    REQUEST = "request"     # 请求消息
    ERROR = "error"         # 错误消息
    HEARTBEAT = "heartbeat"  # 心跳消息


class SubagentState(Enum):
    """Subagent 状态枚举"""
    PENDING = "pending"          # 等待启动
    RUNNING = "running"          # 运行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 执行失败
    CANCELLED = "cancelled"      # 已取消
    TIMEOUT = "timeout"          # 超时


@dataclass
class SubagentMessage:
    """
    Subagent 消息数据结构

    Attributes:
        skill_id: 技能标识
        task_id: 任务标识
        message_type: 消息类型
        payload: 消息内容（字典格式）
        timestamp: 时间戳
        session_id: 会话标识
        correlation_id: 关联ID（用于请求-响应匹配）
    """
    skill_id: str
    task_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime
    session_id: str
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """转换为 JSON 格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubagentMessage':
        """从字典创建消息对象"""
        # 转换 message_type 为枚举
        if isinstance(data.get('message_type'), str):
            data['message_type'] = MessageType(data['message_type'])

        # 转换 timestamp 为 datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'SubagentMessage':
        """从 JSON 字符串创建消息对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @staticmethod
    def create_status_message(
        skill_id: str,
        task_id: str,
        status: SubagentState,
        progress: float = 0.0,
        session_id: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'SubagentMessage':
        """
        创建状态更新消息

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            status: 状态
            progress: 进度（0.0-1.0）
            session_id: 会话标识
            metadata: 附加元数据

        Returns:
            SubagentMessage 对象
        """
        payload = {
            'status': status.value,
            'progress': progress,
            'metadata': metadata or {}
        }
        return SubagentMessage(
            skill_id=skill_id,
            task_id=task_id,
            message_type=MessageType.STATUS,
            payload=payload,
            timestamp=datetime.now(),
            session_id=session_id
        )

    @staticmethod
    def create_result_message(
        skill_id: str,
        task_id: str,
        result: Dict[str, Any],
        success: bool = True,
        session_id: str = "",
        correlation_id: Optional[str] = None
    ) -> 'SubagentMessage':
        """
        创建执行结果消息

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            result: 执行结果
            success: 是否成功
            session_id: 会话标识
            correlation_id: 关联ID

        Returns:
            SubagentMessage 对象
        """
        payload = {
            'result': result,
            'success': success
        }
        return SubagentMessage(
            skill_id=skill_id,
            task_id=task_id,
            message_type=MessageType.RESULT,
            payload=payload,
            timestamp=datetime.now(),
            session_id=session_id,
            correlation_id=correlation_id
        )

    @staticmethod
    def create_request_message(
        skill_id: str,
        task_id: str,
        request_type: str,
        request_data: Dict[str, Any],
        session_id: str = "",
        correlation_id: Optional[str] = None
    ) -> 'SubagentMessage':
        """
        创建请求消息

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            request_type: 请求类型
            request_data: 请求数据
            session_id: 会话标识
            correlation_id: 关联ID

        Returns:
            SubagentMessage 对象
        """
        payload = {
            'request_type': request_type,
            'request_data': request_data
        }
        return SubagentMessage(
            skill_id=skill_id,
            task_id=task_id,
            message_type=MessageType.REQUEST,
            payload=payload,
            timestamp=datetime.now(),
            session_id=session_id,
            correlation_id=correlation_id
        )

    @staticmethod
    def create_error_message(
        skill_id: str,
        task_id: str,
        error_message: str,
        error_code: Optional[int] = None,
        error_type: str = "SubagentError",
        session_id: str = "",
        correlation_id: Optional[str] = None,
        suggestion: Optional[str] = None
    ) -> 'SubagentMessage':
        """
        创建错误消息

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            error_message: 错误消息
            error_code: 错误码
            error_type: 错误类型
            session_id: 会话标识
            correlation_id: 关联ID
            suggestion: 建议的解决方法

        Returns:
            SubagentMessage 对象
        """
        payload = {
            'error_message': error_message,
            'error_code': error_code,
            'error_type': error_type,
            'suggestion': suggestion
        }
        return SubagentMessage(
            skill_id=skill_id,
            task_id=task_id,
            message_type=MessageType.ERROR,
            payload=payload,
            timestamp=datetime.now(),
            session_id=session_id,
            correlation_id=correlation_id
        )

    @staticmethod
    def create_heartbeat_message(
        skill_id: str,
        task_id: str,
        session_id: str = ""
    ) -> 'SubagentMessage':
        """
        创建心跳消息

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            session_id: 会话标识

        Returns:
            SubagentMessage 对象
        """
        return SubagentMessage(
            skill_id=skill_id,
            task_id=task_id,
            message_type=MessageType.HEARTBEAT,
            payload={'timestamp': datetime.now().isoformat()},
            timestamp=datetime.now(),
            session_id=session_id
        )


class MessageQueue:
    """
    消息队列实现

    基于 Python queue 的简单消息队列，用于 subagent 之间的消息传递。
    """

    def __init__(self, max_size: int = 100):
        """
        初始化消息队列

        Args:
            max_size: 队列最大容量
        """
        from queue import Queue
        self._queue: Queue = Queue(maxsize=max_size)
        self._closed = False

    def put(self, message: SubagentMessage, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        将消息放入队列

        Args:
            message: 消息对象
            block: 是否阻塞等待
            timeout: 超时时间（秒）

        Returns:
            是否成功放入队列

        Raises:
            SkillError: 队列已关闭或超时
        """
        if self._closed:
            raise SkillError("Message queue is closed", code=5001)

        try:
            self._queue.put(message, block=block, timeout=timeout)
            return True
        except Exception as e:
            raise SkillError(
                f"Failed to put message into queue: {str(e)}",
                code=5002,
                suggestion="Check if the queue is full or increase max_size"
            )

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[SubagentMessage]:
        """
        从队列获取消息

        Args:
            block: 是否阻塞等待
            timeout: 超时时间（秒）

        Returns:
            消息对象，如果队列已关闭且为空则返回 None

        Raises:
            SkillError: 超时
        """
        try:
            if not block and self._queue.empty():
                return None
            return self._queue.get(block=block, timeout=timeout)
        except Exception as e:
            if self._closed and self._queue.empty():
                return None
            raise SkillError(
                f"Failed to get message from queue: {str(e)}",
                code=5003,
                suggestion="Check if the queue timeout is too short"
            )

    def empty(self) -> bool:
        """检查队列是否为空"""
        return self._queue.empty()

    def qsize(self) -> int:
        """获取队列大小"""
        return self._queue.qsize()

    def close(self):
        """关闭消息队列"""
        self._closed = True

    def __len__(self) -> int:
        return self.qsize()


class MessageRouter:
    """
    消息路由器

    根据 skill_id 和 task_id 路由消息到对应的 subagent。
    """

    def __init__(self):
        """初始化消息路由器"""
        self._queues: Dict[str, MessageQueue] = {}  # key: skill_id:task_id
        self._global_queue = MessageQueue()  # 全局消息队列（广播）

    def register_queue(self, skill_id: str, task_id: str, queue: Optional[MessageQueue] = None) -> MessageQueue:
        """
        注册消息队列

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            queue: 消息队列（如果为 None 则创建新队列）

        Returns:
            消息队列对象
        """
        key = f"{skill_id}:{task_id}"
        if queue is None:
            queue = MessageQueue()
        self._queues[key] = queue
        return queue

    def unregister_queue(self, skill_id: str, task_id: str):
        """
        注销消息队列

        Args:
            skill_id: 技能标识
            task_id: 任务标识
        """
        key = f"{skill_id}:{task_id}"
        if key in self._queues:
            self._queues[key].close()
            del self._queues[key]

    def send(self, message: SubagentMessage, target_queue: Optional[MessageQueue] = None) -> bool:
        """
        发送消息

        Args:
            message: 消息对象
            target_queue: 目标队列（如果为 None 则根据 skill_id:task_id 路由）

        Returns:
            是否发送成功
        """
        if target_queue:
            target_queue.put(message)
            return True

        key = f"{message.skill_id}:{message.task_id}"
        if key in self._queues:
            self._queues[key].put(message)
            # 同时发送到全局队列
            self._global_queue.put(message)
            return True
        else:
            # 只发送到全局队列
            self._global_queue.put(message)
            return False

    def receive(self, skill_id: str, task_id: str, block: bool = True,
                timeout: Optional[float] = None) -> Optional[SubagentMessage]:
        """
        接收消息

        Args:
            skill_id: 技能标识
            task_id: 任务标识
            block: 是否阻塞等待
            timeout: 超时时间（秒）

        Returns:
            消息对象，如果没有则返回 None
        """
        key = f"{skill_id}:{task_id}"
        if key in self._queues:
            return self._queues[key].get(block=block, timeout=timeout)
        return None

    def receive_global(self, block: bool = True,
                       timeout: Optional[float] = None) -> Optional[SubagentMessage]:
        """
        从全局队列接收消息（广播消息）

        Args:
            block: 是否阻塞等待
            timeout: 超时时间（秒）

        Returns:
            消息对象，如果没有则返回 None
        """
        return self._global_queue.get(block=block, timeout=timeout)

    def get_queue(self, skill_id: str, task_id: str) -> Optional[MessageQueue]:
        """
        获取指定队列

        Args:
            skill_id: 技能标识
            task_id: 任务标识

        Returns:
            消息队列对象，如果不存在则返回 None
        """
        key = f"{skill_id}:{task_id}"
        return self._queues.get(key)

    def close(self):
        """关闭消息路由器"""
        for queue in self._queues.values():
            queue.close()
        self._global_queue.close()
        self._queues.clear()
