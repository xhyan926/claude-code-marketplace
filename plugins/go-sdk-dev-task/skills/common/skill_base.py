"""
技能基类

定义统一的技能执行接口，所有技能应继承此类。
集成 Google Go 规范、LSP 支持和命名规范验证。
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any, List
from abc import ABC, abstractmethod

from .logger import get_logger
from .error_handler import ErrorHandler
from .config import Config
from .validators import Validator
from .lsp_support import LSPSupport
from .naming_standards import NamingValidator, GoNamingStandards, NamingCategory


class SkillBase(ABC):
    """技能基类"""

    def __init__(self):
        """初始化技能基类"""
        self.logger = get_logger(self.__class__.__name__)
        self.error_handler = ErrorHandler()
        self.validator = Validator()
        self.config = Config()

        # Google Go 规范支持
        self.lsp_support = LSPSupport(str(Path(__file__).parent.parent.parent.parent))
        self.naming_validator = NamingValidator()
        self.naming_standards = GoNamingStandards()

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
        验证输入参数并执行 Google Go 规范检查

        Args:
            context: 执行上下文

        Returns:
            bool: 验证结果
        """
        # 基础验证
        if not super().validate(context):
            return False

        # Google Go 规范验证
        if not self._validate_go_standards(context):
            return False

        return True

    def _validate_go_standards(self, context: Dict[str, Any]) -> bool:
        """
        验证 Google Go 规范符合性

        Args:
            context: 执行上下文

        Returns:
            bool: 验证结果
        """
        try:
            # 检查命名规范
            if 'function_name' in context:
                func_name = context['function_name']
                is_valid, errors = self.naming_standards.validate_function_name(func_name)
                if not is_valid:
                    self.logger.error(f"函数名 '{func_name}' 不符合 Google 规范: {errors}")
                    return False

            if 'package_name' in context:
                pkg_name = context['package_name']
                is_valid, errors = self.naming_standards.validate_package_name(pkg_name)
                if not is_valid:
                    self.logger.error(f"包名 '{pkg_name}' 不符合 Google 规范: {errors}")
                    return False

            # 验证 LSP 友好性（如果有代码生成）
            if 'generated_code' in context:
                code = context['generated_code']
                is_valid, errors = self.lsp_support.validate_lsp_friendly_code(code)
                if not is_valid:
                    self.logger.error(f"生成的代码不符合 LSP 友好规范: {errors}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Google 规范验证失败: {e}")
            return False

    def generate_go_doc_comment(self, description: str, params: List[Dict] = None, returns: List[Dict] = None, examples: List[str] = None) -> str:
        """
        生成 Google 标准的文档注释

        Args:
            description: 函数描述
            params: 参数列表，每个参数包含 name 和 description
            returns: 返回值列表，每个返回值包含 type 和 description
            examples: 使用示例列表

        Returns:
            str: 生成的文档注释
        """
        comment_lines = [f"// {description}"]

        if params:
            comment_lines.append("//")
            comment_lines.append("// 参数:")
            for param in params:
                comment_lines.append(f"//   {param['name']}: {param['description']}")

        if returns:
            comment_lines.append("//")
            comment_lines.append("// 返回值:")
            for ret in returns:
                comment_lines.append(f"//   {ret['type']}: {ret['description']}")

        if examples:
            comment_lines.append("//")
            comment_lines.append("// 示例:")
            for example in examples:
                comment_lines.append(f"// {example}")

        return "\n".join(comment_lines)

    def standardize_error_handling(self, code: str) -> str:
        """
        标准化错误处理，使用 %w 包装错误

        Args:
            code: 原始代码

        Returns:
            str: 标准化后的代码
        """
        # 替换简单错误包装
        code = re.sub(r'return\s+fmt\.Errorf\([^)]+\)',
                      lambda m: self._wrap_error_with_context(m.group()),
                      code)

        # 替换字符串比较错误类型
        code = re.sub(r'err\.Error\(\s*==\s*["\'][^"\']*["\']',
                      lambda m: f'errors.Is({m.group().split("=")[0]}, errors.New({m.group().split("=")[1].strip()}))',
                      code)

        return code

    def _wrap_error_with_context(self, match: str) -> str:
        """
        包装错误以添加上下文信息
        """
        # 简化实现，实际项目中需要更复杂的错误包装逻辑
        return match.replace('fmt.Errorf(', 'fmt.Errorf("context: %w", ')

    def cleanup(self, context: Dict[str, Any]) -> None:
        """
        清理资源

        Args:
            context: 执行上下文
        """
        # 清理 LSP 临时文件
        if 'lsp_temp_files' in context:
            for temp_file in context['lsp_temp_files']:
                try:
                    Path(temp_file).unlink()
                except Exception as e:
                    self.logger.warning(f"清理临时文件失败: {temp_file}, 错误: {e}")

        # 调用父类清理方法
        super().cleanup(context)

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

    def write_file(self, file_path: Path, content: str, validate_lsp: bool = True) -> bool:
        """
        写入文件内容，可选 LSP 验证

        Args:
            file_path: 文件路径
            content: 文件内容
            validate_lsp: 是否进行 LSP 验证

        Returns:
            bool: 写入是否成功
        """
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"文件写入成功: {file_path}")

            # LSP 验证
            if validate_lsp:
                lsp_result = self.lsp_support.check_lsp_compatibility(str(file_path))
                if not lsp_result['valid']:
                    self.logger.warning(f"LSP 验证发现问题: {lsp_result['errors']}")
                    self.logger.info("LSP 优化建议: " + "\n".join(lsp_result['recommendations']))

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
