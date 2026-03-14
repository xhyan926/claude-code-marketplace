"""
验证器模块

提供常用的验证功能，集成 Google Go 规范和 LSP 检查。
"""

from pathlib import Path
from typing import Any, List, Optional, Dict, Callable
import re

from .error_handler import ValidationError
from .lsp_support import LSPSupport
from .naming_standards import GoNamingStandards, NamingCategory


class Validator:
    """验证器"""

    # Google Go 规范和 LSP 支持实例
    lsp_support = None
    naming_standards = None

    @classmethod
    def initialize_go_standards(cls, project_root: str = None):
        """初始化 Google Go 规范支持

        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            from pathlib import Path
            project_root = str(Path(__file__).parent.parent.parent.parent)

        cls.lsp_support = LSPSupport(project_root)
        cls.naming_standards = GoNamingStandards()

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

    # ===== Google Go 规范验证方法 =====

    @classmethod
    def validate_go_package_name(cls, package_name: str) -> None:
        """验证 Go 包名符合 Google Go 规范

        Args:
            package_name: 包名

        Raises:
            ValidationError: 验证失败
        """
        if cls.naming_standards is None:
            cls.initialize_go_standards()

        is_valid, errors = cls.naming_standards.validate_package_name(package_name)
        if not is_valid:
            raise ValidationError(
                f"包名 '{package_name}' 不符合 Google Go 规范: {', '.join(errors)}",
                "package_name"
            )

    @classmethod
    def validate_go_function_name(cls, function_name: str, is_public: bool = True) -> None:
        """验证 Go 函数名符合 Google Go 规范

        Args:
            function_name: 函数名
            is_public: 是否为公共函数

        Raises:
            ValidationError: 验证失败
        """
        if cls.naming_standards is None:
            cls.initialize_go_standards()

        category = NamingCategory.FUNCTION if is_public else NamingCategory.VARIABLE
        is_valid, errors = cls.naming_standards.validate_function_name(function_name, category)
        if not is_valid:
            raise ValidationError(
                f"函数名 '{function_name}' 不符合 Google Go 规范: {', '.join(errors)}",
                "function_name"
            )

    @classmethod
    def validate_go_variable_name(cls, variable_name: str) -> None:
        """验证 Go 变量名符合 Google Go 规范

        Args:
            variable_name: 变量名

        Raises:
            ValidationError: 验证失败
        """
        if cls.naming_standards is None:
            cls.initialize_go_standards()

        is_valid, errors = cls.naming_standards.validate_variable_name(variable_name)
        if not is_valid:
            raise ValidationError(
                f"变量名 '{variable_name}' 不符合 Google Go 规范: {', '.join(errors)}",
                "variable_name"
            )

    @classmethod
    def validate_go_constant_name(cls, constant_name: str) -> None:
        """验证 Go 常量名符合 Google Go 规范

        Args:
            constant_name: 常量名

        Raises:
            ValidationError: 验证失败
        """
        if cls.naming_standards is None:
            cls.initialize_go_standards()

        is_valid, errors = cls.naming_standards.validate_constant_name(constant_name)
        if not is_valid:
            raise ValidationError(
                f"常量名 '{constant_name}' 不符合 Google Go 规范: {', '.join(errors)}",
                "constant_name"
            )

    @classmethod
    def validate_go_code_lsp_friendly(cls, code: str, file_path: str = None) -> None:
        """验证 Go 代码符合 LSP 友好规范

        Args:
            code: Go 代码
            file_path: 文件路径（可选）

        Raises:
            ValidationError: 验证失败
        """
        if cls.lsp_support is None:
            cls.initialize_go_standards()

        is_valid, errors = cls.lsp_support.validate_lsp_friendly_code(code)
        if not is_valid:
            field_name = "code" if file_path is None else file_path
            raise ValidationError(
                f"代码不符合 LSP 友好规范: {', '.join(errors)}",
                field_name
            )

    @classmethod
    def validate_go_file_lsp_friendly(cls, file_path: Path) -> None:
        """验证 Go 文件符合 LSP 友好规范

        Args:
            file_path: 文件路径

        Raises:
            ValidationError: 验证失败
        """
        if cls.lsp_support is None:
            cls.initialize_go_standards()

        result = cls.lsp_support.check_lsp_compatibility(str(file_path))
        if not result['valid']:
            raise ValidationError(
                f"文件 '{file_path}' 不符合 LSP 友好规范: {', '.join(result['errors'])}",
                str(file_path)
            )

    @classmethod
    def validate_go_doc_comment(cls, code: str) -> None:
        """验证 Go 文档注释符合 godoc 标准

        Args:
            code: Go 代码

        Raises:
            ValidationError: 验证失败
        """
        # 检查是否有导出函数缺少文档注释
        export_pattern = r'func ([A-Z][a-zA-Z0-9_]*)\('
        doc_pattern = r'// \1 [^\n]'

        exports = re.findall(export_pattern, code)
        for func_name in exports:
            doc_check = re.search(doc_pattern.replace('\\1', func_name), code)
            if doc_check is None:
                raise ValidationError(
                    f"导出函数 '{func_name}' 缺少文档注释",
                    "doc_comments"
                )

    @classmethod
    def validate_go_error_handling(cls, code: str) -> None:
        """验证 Go 错误处理符合 Google Go 规范

        Args:
            code: Go 代码

        Raises:
            ValidationError: 验证失败
        """
        # 检查是否使用字符串比较错误类型
        string_comparison_pattern = r'err\.Error\(\s*==\s*["\'][^"\']*["\']'
        matches = re.findall(string_comparison_pattern, code)

        if matches:
            raise ValidationError(
                f"发现 {len(matches)} 处使用字符串比较错误类型，应使用 errors.Is() 或 errors.As()",
                "error_handling"
            )

        # 检查是否缺少错误包装
        simple_return_pattern = r'return\s+err\s*$'
        matches = re.finditer(simple_return_pattern, code, re.MULTILINE)

        for match in matches:
            line_start = code.rfind('\n', 0, match.start()) + 1
            line_end = code.find('\n', match.end())
            line = code[line_start:line_end if line_end != -1 else len(code)]

            # 检查这行是否已经有错误包装
            if '%w' not in line and 'errors.Is' not in line:
                raise ValidationError(
                    f"发现未包装的错误返回，建议使用 fmt.Errorf(\"...: %w\", err)",
                    "error_handling"
                )

    # ===== Go 测试规范验证方法 =====

    @classmethod
    def validate_go_test_bdd_naming(cls, test_name: str) -> None:
        """验证 Go 测试命名符合 BDD 规范

        Args:
            test_name: 测试函数名

        Raises:
            ValidationError: 验证失败
        """
        # BDD 命名模式: Test{Function}_Should{Result}_When{Condition}_Given{Precondition}
        bdd_pattern = r'^Test[A-Z][a-zA-Z0-9_]*_Should[A-Z][a-zA-Z0-9_]*_When[A-Z][a-zA-Z0-9_]*(?:_Given[A-Z][a-zA-Z0-9_]*)?$'

        if not re.match(bdd_pattern, test_name):
            raise ValidationError(
                f"测试名 '{test_name}' 不符合 BDD 命名规范，格式应为: TestFunction_ShouldResult_WhenCondition_GivenPrecondition",
                "test_name"
            )

    @classmethod
    def validate_go_test_structure(cls, test_code: str) -> None:
        """验证 Go 测试代码结构符合最佳实践

        Args:
            test_code: 测试代码

        Raises:
            ValidationError: 验证失败
        """
        # 检查是否使用 t.Cleanup() 而非 defer
        if 'defer ' in test_code and 't.Cleanup' not in test_code:
            # 只在需要清理资源的情况下警告
            if any(keyword in test_code for keyword in ['Close()', 'Reset()', 'stop()']):
                raise ValidationError(
                    "建议使用 t.Cleanup() 替代 defer 进行资源清理",
                    "test_structure"
                )

    # ===== 综合验证方法 =====

    @classmethod
    def validate_go_code_comprehensive(
        cls,
        code: str,
        validate_lsp: bool = True,
        validate_docs: bool = True,
        validate_errors: bool = True
    ) -> List[str]:
        """综合验证 Go 代码符合所有 Google Go 规范

        Args:
            code: Go 代码
            validate_lsp: 是否验证 LSP 友好性
            validate_docs: 是否验证文档注释
            validate_errors: 是否验证错误处理

        Returns:
            List[str]: 验证错误列表
        """
        all_errors = []

        if validate_lsp:
            try:
                cls.validate_go_code_lsp_friendly(code)
            except ValidationError as e:
                all_errors.append(str(e))

        if validate_docs:
            try:
                cls.validate_go_doc_comment(code)
            except ValidationError as e:
                all_errors.append(str(e))

        if validate_errors:
            try:
                cls.validate_go_error_handling(code)
            except ValidationError as e:
                all_errors.append(str(e))

        return all_errors

    @classmethod
    def validate_go_file_comprehensive(
        cls,
        file_path: Path,
        validate_lsp: bool = True,
        validate_docs: bool = True,
        validate_errors: bool = True
    ) -> List[str]:
        """综合验证 Go 文件符合所有 Google Go 规范

        Args:
            file_path: 文件路径
            validate_lsp: 是否验证 LSP 友好性
            validate_docs: 是否验证文档注释
            validate_errors: 是否验证错误处理

        Returns:
            List[str]: 验证错误列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            return cls.validate_go_code_comprehensive(code, validate_lsp, validate_docs, validate_errors)

        except FileNotFoundError:
            raise ValidationError(f"文件不存在: {file_path}", "file_path")
        except Exception as e:
            raise ValidationError(f"读取文件失败: {str(e)}", "file_path")
