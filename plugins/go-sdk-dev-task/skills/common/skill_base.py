"""
技能基类

定义统一的技能执行接口，所有技能应继承此类。
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

from .logger import get_logger
from .error_handler import ErrorHandler
from .config import Config
from .validators import Validator


class SkillBase(ABC):
    """技能基类"""

    def __init__(self):
        """初始化技能基类"""
        self.logger = get_logger(self.__class__.__name__)
        self.error_handler = ErrorHandler()
        self.validator = Validator()
        self.config = Config()

        # 技能路径
        self.skill_path = Path(__file__).parent.parent

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能

        Args:
            context: 执行上下文，包含输入参数和状态信息

        Returns:
            Dict[str, Any]: 执行结果，包含状态和输出数据
        """
        pass

    def validate(self, context: Dict[str, Any]) -> bool:
        """
        验证输入参数

        Args:
            context: 执行上下文

        Returns:
            bool: 验证结果
        """
        return True

    def cleanup(self, context: Dict[str, Any]) -> None:
        """
        清理资源

        Args:
            context: 执行上下文
        """
        pass

    def get_template_path(self, template_name: str) -> Path:
        """
        获取模板文件路径

        Args:
            template_name: 模板文件名

        Returns:
            Path: 模板文件路径
        """
        template_path = self.skill_path / "templates" / template_name
        if not template_path.exists():
            # 尝试使用共享模板
            shared_path = self.skill_path.parent.parent / "templates" / "common" / template_name
            if shared_path.exists():
                return shared_path
        return template_path

    def read_file(self, file_path: Path) -> Optional[str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            Optional[str]: 文件内容，如果文件不存在返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"文件不存在: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"读取文件失败: {file_path}, 错误: {e}")
            return None

    def write_file(self, file_path: Path, content: str) -> bool:
        """
        写入文件内容

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            bool: 写入是否成功
        """
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"文件写入成功: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"写入文件失败: {file_path}, 错误: {e}")
            return False

    def ensure_directory(self, dir_path: Path) -> bool:
        """
        确保目录存在

        Args:
            dir_path: 目录路径

        Returns:
            bool: 创建是否成功
        """
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"目录已创建/存在: {dir_path}")
            return True
        except Exception as e:
            self.logger.error(f"创建目录失败: {dir_path}, 错误: {e}")
            return False

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行技能（包含验证、执行、清理的完整流程）

        Args:
            context: 执行上下文

        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            self.logger.info(f"开始执行技能: {self.__class__.__name__}")

            # 验证输入
            if not self.validate(context):
                raise ValueError("输入验证失败")

            # 执行技能
            result = self.execute(context)

            # 清理资源
            self.cleanup(context)

            self.logger.info(f"技能执行完成: {self.__class__.__name__}")
            return result

        except Exception as e:
            self.logger.error(f"技能执行失败: {self.__class__.__name__}, 错误: {e}")
            self.error_handler.handle(e)
            return {
                "status": "error",
                "error": str(e)
            }
