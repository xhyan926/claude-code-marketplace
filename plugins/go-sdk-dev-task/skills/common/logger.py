"""
日志记录模块

提供结构化日志记录功能。
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """JSON 格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON

        Args:
            record: 日志记录

        Returns:
            str: JSON 格式的日志
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色控制台格式化器"""

    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为彩色文本

        Args:
            record: 日志记录

        Returns:
            str: 彩色格式的日志
        """
        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET

        # 格式化日志
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname.ljust(8)
        logger_name = record.name.ljust(20)
        message = record.getMessage()

        # 添加颜色
        log_line = (
            f"{timestamp} | {color}{level}{reset} | "
            f"{logger_name} | {message}"
        )

        # 添加位置信息
        if record.levelno >= logging.WARNING:
            log_line += f" ({record.module}:{record.funcName}:{record.lineno})"

        return log_line


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        json_format: 是否使用 JSON 格式

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 清除现有的处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    # 文件处理器（如果指定）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
                )
            )
        logger.addHandler(file_handler)

    return logger


def get_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称，默认为调用模块名
        level: 日志级别
        log_file: 日志文件路径
        json_format: 是否使用 JSON 格式

    Returns:
        logging.Logger: 日志记录器
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', '__main__')

    return setup_logger(name, level, log_file, json_format)


class Logger:
    """日志记录器类（兼容旧接口）"""

    def __init__(self, name: str):
        """
        初始化日志记录器

        Args:
            name: 日志记录器名称
        """
        self._logger = get_logger(name)

    def debug(self, message: str) -> None:
        """记录调试信息"""
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """记录信息"""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """记录警告"""
        self._logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:
        """记录错误"""
        self._logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False) -> None:
        """记录严重错误"""
        self._logger.critical(message, exc_info=exc_info)

    def exception(self, message: str) -> None:
        """记录异常"""
        self._logger.exception(message)
