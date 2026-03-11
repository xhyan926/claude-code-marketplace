"""
Go SDK 开发技能通用框架

提供统一的技能实现基类、模板引擎、错误处理、日志记录、配置管理和验证器。
"""

from .skill_base import SkillBase
from .template_engine import TemplateEngine
from .error_handler import ErrorHandler, SkillError
from .logger import get_logger
from .config import Config
from .validators import Validator
from .error_codes import ErrorCodes

__all__ = [
    'SkillBase',
    'TemplateEngine',
    'ErrorHandler',
    'SkillError',
    'get_logger',
    'Config',
    'Validator',
    'ErrorCodes',
]

__version__ = '1.0.0'
