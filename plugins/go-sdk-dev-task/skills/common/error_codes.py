"""
错误码定义

定义所有技能的错误码。
"""

import json
from pathlib import Path
from typing import Dict, Any


class ErrorCodes:
    """错误码类"""
    """错误码类"""

    # 错误码范围
    SKILL_ERROR_BASE = 1000
    VALIDATION_ERROR_BASE = 1000
    TEMPLATE_ERROR_BASE = 2000
    FILESYSTEM_ERROR_BASE = 3000
    DEPENDENCY_ERROR_BASE = 4000
    SKILL_EXECUTION_ERROR_BASE = 5000

    # 技能错误
    SKILL_ERROR = 1000

    # 验证错误
    VALIDATION_ERROR = 1001
    INVALID_INPUT_ERROR = 1002
    MISSING_REQUIRED_FIELD_ERROR = 1003

    # 模板错误
    TEMPLATE_ERROR = 2000
    TEMPLATE_SYNTAX_ERROR = 2001
    TEMPLATE_NOT_FOUND_ERROR = 2002
    TEMPLATE_RENDER_ERROR = 2003

    # 文件系统错误
    FILESYSTEM_ERROR = 3000
    FILE_NOT_FOUND_ERROR = 3001
    FILE_WRITE_ERROR = 3002
    DIRECTORY_NOT_FOUND_ERROR = 3003
    DIRECTORY_CREATE_ERROR = 3004
    PERMISSION_ERROR = 3005

    # 依赖错误
    DEPENDENCY_ERROR = 4000
    DEPENDENCY_NOT_FOUND_ERROR = 4001
    DEPENDENCY_VERSION_MISMATCH = 4002

    # 技能执行错误
    SKILL_EXECUTION_ERROR = 5000
    CONFIG_ERROR = 5001
    TIMEOUT_ERROR = 5002
    EXECUTION_FAILED_ERROR = 5003

    # 错误消息映射
    ERROR_MESSAGES: Dict[int, str] = {
        SKILL_ERROR: "技能执行错误",
        VALIDATION_ERROR: "验证错误",
        INVALID_INPUT_ERROR: "无效的输入",
        MISSING_REQUIRED_FIELD_ERROR: "缺少必需字段",
        TEMPLATE_ERROR: "模板错误",
        TEMPLATE_SYNTAX_ERROR: "模板语法错误",
        TEMPLATE_NOT_FOUND_ERROR: "模板文件不存在",
        TEMPLATE_RENDER_ERROR: "模板渲染失败",
        FILESYSTEM_ERROR: "文件系统错误",
        FILE_NOT_FOUND_ERROR: "文件未找到",
        FILE_WRITE_ERROR: "文件写入失败",
        DIRECTORY_NOT_FOUND_ERROR: "目录未找到",
        DIRECTORY_CREATE_ERROR: "目录创建失败",
        PERMISSION_ERROR: "权限错误",
        DEPENDENCY_ERROR: "依赖错误",
        DEPENDENCY_NOT_FOUND_ERROR: "依赖未找到",
        DEPENDENCY_VERSION_MISMATCH: "依赖版本不匹配",
        SKILL_EXECUTION_ERROR: "技能执行错误",
        CONFIG_ERROR: "配置错误",
        TIMEOUT_ERROR: "执行超时",
        EXECUTION_FAILED_ERROR: "执行失败",
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        """
        获取错误消息

        Args:
            code: 错误码

        Returns:
            str: 错误消息
        """
        return cls.ERROR_MESSAGES.get(code, "未知错误")

    @classmethod
    def from_file(cls, file_path: Path) -> Dict[str, Any]:
        """
        从文件加载错误码

        Args:
            file_path: 错误码文件路径

        Returns:
            Dict[str, Any]: 错误码字典
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def to_file(cls, file_path: Path, error_codes: Dict[str, Any]) -> None:
        """
        保存错误码到文件

        Args:
            file_path: 错误码文件路径
            error_codes: 错误码字典
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(error_codes, f, indent=2, ensure_ascii=False)

# 创建 ERROR_CODES 常量以保持向后兼容
ERROR_CODES = {
    'SKILL_ERROR': ErrorCodes.SKILL_ERROR,
    'VALIDATION_ERROR': ErrorCodes.VALIDATION_ERROR,
    'INVALID_INPUT_ERROR': ErrorCodes.INVALID_INPUT_ERROR,
    'MISSING_REQUIRED_FIELD_ERROR': ErrorCodes.MISSING_REQUIRED_FIELD_ERROR,
    'TEMPLATE_ERROR': ErrorCodes.TEMPLATE_ERROR,
    'TEMPLATE_SYNTAX_ERROR': ErrorCodes.TEMPLATE_SYNTAX_ERROR,
    'TEMPLATE_NOT_FOUND_ERROR': ErrorCodes.TEMPLATE_NOT_FOUND_ERROR,
    'TEMPLATE_RENDER_ERROR': ErrorCodes.TEMPLATE_RENDER_ERROR,
    'FILESYSTEM_ERROR': ErrorCodes.FILESYSTEM_ERROR,
    'FILE_NOT_FOUND_ERROR': ErrorCodes.FILE_NOT_FOUND_ERROR,
    'FILE_WRITE_ERROR': ErrorCodes.FILE_WRITE_ERROR,
    'DIRECTORY_NOT_FOUND_ERROR': ErrorCodes.DIRECTORY_NOT_FOUND_ERROR,
    'DIRECTORY_CREATE_ERROR': ErrorCodes.DIRECTORY_CREATE_ERROR,
    'PERMISSION_ERROR': ErrorCodes.PERMISSION_ERROR,
    'DEPENDENCY_ERROR': ErrorCodes.DEPENDENCY_ERROR,
    'DEPENDENCY_NOT_FOUND_ERROR': ErrorCodes.DEPENDENCY_NOT_FOUND_ERROR,
    'DEPENDENCY_VERSION_MISMATCH': ErrorCodes.DEPENDENCY_VERSION_MISMATCH,
    'SKILL_EXECUTION_ERROR': ErrorCodes.SKILL_EXECUTION_ERROR,
    'CONFIG_ERROR': ErrorCodes.CONFIG_ERROR,
    'TIMEOUT_ERROR': ErrorCodes.TIMEOUT_ERROR,
    'EXECUTION_FAILED_ERROR': ErrorCodes.EXECUTION_FAILED_ERROR,
}
