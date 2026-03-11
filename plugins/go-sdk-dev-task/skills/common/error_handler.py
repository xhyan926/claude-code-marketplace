"""
错误处理模块

提供统一的错误码体系和错误处理机制。
"""

import sys
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, Type
from functools import wraps

from .error_codes import ERROR_CODES


def load_error_codes() -> Dict[str, Dict[str, Any]]:
    """加载错误码定义"""
    error_codes_path = Path(__file__).parent / "error_codes.json"
    with open(error_codes_path, 'r', encoding='utf-8') as f:
        return json.load(f)


ERROR_CODES = load_error_codes()


class SkillError(Exception):
    """技能错误基类"""

    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        suggestion: Optional[str] = None,
        location: Optional[str] = None
    ):
        """
        初始化技能错误

        Args:
            message: 错误消息
            code: 错误码
            suggestion: 建议的解决方法
            location: 错误位置
        """
        self.message = message
        self.code = code
        self.suggestion = suggestion
        self.location = location
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
            "location": self.location,
        }


class ValidationError(SkillError):
    """验证错误"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("ValidationError", {}).get("code", 1001),
            suggestion=f"请检查字段 '{field}' 的值是否正确" if field else None
        )
        self.field = field


class TemplateError(SkillError):
    """模板错误"""

    def __init__(self, message: str, template_name: Optional[str] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("TemplateError", {}).get("code", 2000),
            suggestion=f"请检查模板文件 '{template_name}' 的语法" if template_name else None
        )
        self.template_name = template_name


class FileSystemError(SkillError):
    """文件系统错误"""

    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("FileSystemError", {}).get("code", 3000),
            suggestion=f"请检查文件路径 '{file_path}' 是否正确" if file_path else None
        )
        self.file_path = file_path


class DependencyError(SkillError):
    """依赖错误"""

    def __init__(self, message: str, dependency: Optional[str] = None, required_tasks: Optional[list] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("DependencyError", {}).get("code", 4000),
            suggestion=f"请先完成任务: {', '.join(required_tasks or [])}" if required_tasks else None
        )
        self.dependency = dependency
        self.required_tasks = required_tasks or []


class SkillExecutionError(SkillError):
    """技能执行错误"""

    def __init__(self, message: str, skill_name: Optional[str] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("SkillExecutionError", {}).get("code", 5000),
            suggestion=f"请检查技能 '{skill_name}' 的配置和输入" if skill_name else None
        )
        self.skill_name = skill_name


class ConfigError(SkillError):
    """配置错误"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("ConfigError", {}).get("code", 5001),
            suggestion=f"请检查配置项 '{config_key}' 的值" if config_key else None
        )
        self.config_key = config_key


class TimeoutError(SkillError):
    """超时错误"""

    def __init__(self, message: str, timeout: Optional[float] = None):
        super().__init__(
            message,
            code=ERROR_CODES.get("TimeoutError", {}).get("code", 5002),
            suggestion=f"操作超时（{timeout}秒），请检查网络连接或增加超时时间" if timeout else None
        )
        self.timeout = timeout


class ErrorHandler:
    """错误处理器"""

    def __init__(self, log_errors: bool = True):
        """
        初始化错误处理器

        Args:
            log_errors: 是否记录错误日志
        """
        self.log_errors = log_errors

    def handle(self, error: Exception) -> None:
        """
        处理错误

        Args:
            error: 异常对象
        """
        if isinstance(error, SkillError):
            self._handle_skill_error(error)
        else:
            self._handle_generic_error(error)

    def _handle_skill_error(self, error: SkillError) -> None:
        """
        处理技能错误

        Args:
            error: 技能错误
        """
        error_info = error.to_dict()

        # 构建友好的错误信息
        lines = []
        lines.append(f"❌ {error.__class__.__name__}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"{error.message}")

        if error.suggestion:
            lines.append("")
            lines.append("💡 建议解决方法：")
            lines.append(error.suggestion)

        if error.location:
            lines.append("")
            lines.append(f"📍 位置: {error.location}")

        error_text = "\n".join(lines)

        if self.log_errors:
            from .logger import get_logger
            logger = get_logger("ErrorHandler")
            logger.error(error_text)

        # 打印到标准错误
        print(error_text, file=sys.stderr)

    def _handle_generic_error(self, error: Exception) -> None:
        """
        处理通用错误

        Args:
            error: 异常对象
        """
        lines = []
        lines.append("❌ 未知错误")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"{type(error).__name__}: {error}")

        error_text = "\n".join(lines)

        if self.log_errors:
            from .logger import get_logger
            logger = get_logger("ErrorHandler")
            logger.error(error_text, exc_info=True)

        print(error_text, file=sys.stderr)

    @staticmethod
    def format_friendly_error(error: SkillError) -> str:
        """
        格式化友好的错误信息

        Args:
            error: 技能错误

        Returns:
            str: 格式化后的错误信息
        """
        lines = []
        lines.append(f"❌ {error.__class__.__name__}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(error.message)

        if error.suggestion:
            lines.append("")
            lines.append("💡 建议解决方法：")
            lines.append(error.suggestion)

        if error.location:
            lines.append("")
            lines.append(f"📍 位置: {error.location}")

        return "\n".join(lines)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential: 是否使用指数退避
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from .logger import get_logger
            logger = get_logger(func.__name__)

            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f"重试 {max_attempts} 次后仍然失败")
                        raise

                    delay = base_delay
                    if exponential:
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

                    logger.warning(
                        f"第 {attempt} 次尝试失败: {e}，"
                        f"{delay:.1f} 秒后重试..."
                    )
                    time.sleep(delay)

            raise last_exception
        return wrapper
    return decorator


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    error_types: Optional[Type[SkillError]] = None
):
    """
    简化的重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 延迟（秒）
        error_types: 需要重试的错误类型
    """
    return with_retry(max_attempts, delay, delay, exponential=False, exceptions=error_types or (Exception,))
