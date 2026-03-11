"""
验证器模块

提供常用的验证功能。
"""

from pathlib import Path
from typing import Any, List, Optional, Dict, Callable
import re

from .error_handler import ValidationError


class Validator:
    """验证器"""

    @staticmethod
    def not_empty(value: Any, field_name: str = "value") -> None:
        """
        验证值不为空

        Args:
            value: 要验证的值
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if value is None or value == "":
            raise ValidationError(f"{field_name} 不能为空", field_name)

    @staticmethod
    def is_valid_path(path: Path, field_name: str = "path") -> None:
        """
        验证路径有效

        Args:
            path: 路径
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(path, Path):
            raise ValidationError(f"{field_name} 必须是 Path 对象", field_name)

    @staticmethod
    def file_exists(file_path: Path, field_name: str = "file") -> None:
        """
        验证文件存在

        Args:
            file_path: 文件路径
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not file_path.exists():
            raise ValidationError(f"{field_name} 不存在: {file_path}", field_name)

    @staticmethod
    def directory_exists(dir_path: Path, field_name: str = "directory") -> None:
        """
        验证目录存在

        Args:
            dir_path: 目录路径
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not dir_path.exists():
            raise ValidationError(f"{field_name} 不存在: {dir_path}", field_name)

        if not dir_path.is_dir():
            raise ValidationError(f"{field_name} 不是目录: {dir_path}", field_name)

    @staticmethod
    def is_valid_status(status: str) -> bool:
        """
        验证状态值

        Args:
            status: 状态值

        Returns:
            bool: 是否有效
        """
        valid_statuses = ['pending', 'in_progress', 'completed', 'blocked']
        return status in valid_statuses

    @staticmethod
    def validate_status(status: str, field_name: str = "status") -> None:
        """
        验证状态值（抛出异常）

        Args:
            status: 状态值
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not Validator.is_valid_status(status):
            raise ValidationError(
                f"{field_name} 必须是以下值之一: pending, in_progress, completed, blocked",
                field_name
            )

    @staticmethod
    def is_valid_task_id(task_id: str) -> bool:
        """
        验证任务 ID 格式

        Args:
            task_id: 任务 ID

        Returns:
            bool: 是否有效
        """
        return re.match(r'^task-\d+$', task_id) is not None

    @staticmethod
    def validate_task_id(task_id: str, field_name: str = "task_id") -> None:
        """
        验证任务 ID 格式（抛出异常）

        Args:
            task_id: 任务 ID
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not Validator.is_valid_task_id(task_id):
            raise ValidationError(
                f"{field_name} 格式无效，应为 task-01, task-02 等",
                field_name
            )

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            bool: 是否有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        验证 URL 格式

        Args:
            url: URL

        Returns:
            bool: 是否有效
        """
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None

    @staticmethod
    def validate_url(url: str, field_name: str = "url") -> None:
        """
        验证 URL 格式（抛出异常）

        Args:
            url: URL
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not Validator.is_valid_url(url):
            raise ValidationError(
                f"{field_name} 格式无效，应为有效的 HTTP/HTTPS URL",
                field_name
            )

    @staticmethod
    def is_valid_version(version: str) -> bool:
        """
        验证语义化版本号格式

        Args:
            version: 版本号

        Returns:
            bool: 是否有效
        """
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9-]+)?$'
        return re.match(pattern, version) is not None

    @staticmethod
    def validate_range(
        value: int,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        field_name: str = "value"
    ) -> None:
        """
        验证值在指定范围内

        Args:
            value: 值
            min_value: 最小值
            max_value: 最大值
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"{field_name} 不能小于 {min_value}",
                field_name
            )

        if max_value is not None and value > max_value:
            raise ValidationError(
                f"{field_name} 不能大于 {max_value}",
                field_name
            )

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> None:
        """
        验证必需字段存在

        Args:
            data: 数据字典
            required_fields: 必需字段列表

        Raises:
            ValidationError: 验证失败
        """
        missing_fields = [f for f in required_fields if f not in data or data[f] is None]
        if missing_fields:
            raise ValidationError(
                f"缺少必需字段: {', '.join(missing_fields)}",
                field_name=", ".join(missing_fields)
            )

    @staticmethod
    def validate_file_structure(
        dir_path: Path,
        required_files: List[str],
        field_name: str = "directory"
    ) -> None:
        """
        验证目录包含必需文件

        Args:
            dir_path: 目录路径
            required_files: 必需文件列表
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        missing_files = []
        for filename in required_files:
            file_path = dir_path / filename
            if not file_path.exists():
                missing_files.append(filename)

        if missing_files:
            raise ValidationError(
                f"{field_name} 缺少必需文件: {', '.join(missing_files)}",
                field_name=field_name
            )

    @staticmethod
    def validate_subtask_files(
        task_path: Path,
        required_files: Optional[List[str]] = None
    ) -> None:
        """
        验证子任务目录结构

        Args:
            task_path: 子任务路径
            required_files: 必需文件列表，默认为标准子任务文件

        Raises:
            ValidationError: 验证失败
        """
        if required_files is None:
            required_files = [
                "TASK.md",
                "IMPLEMENTATION.md",
                "TEST_PLAN.md"
            ]

        Validator.validate_file_structure(task_path, required_files, "子任务目录")

    @staticmethod
    def custom_validator(
        value: Any,
        validator: Callable[[Any], bool],
        error_message: str,
        field_name: str = "value"
    ) -> None:
        """
        自定义验证器

        Args:
            value: 要验证的值
            validator: 验证函数，返回 bool
            error_message: 错误消息
            field_name: 字段名称

        Raises:
            ValidationError: 验证失败
        """
        if not validator(value):
            raise ValidationError(error_message, field_name)
