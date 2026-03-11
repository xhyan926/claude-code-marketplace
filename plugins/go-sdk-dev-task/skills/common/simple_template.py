"""
简化模板引擎

不依赖外部库的简单模板实现。
"""

from pathlib import Path
from typing import Dict, Any, Optional
import re


class TemplateError(Exception):
    """模板错误"""
    pass


class SimpleTemplateEngine:
    """简化的模板引擎"""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        初始化模板引擎

        Args:
            template_dir: 模板目录路径，默认为 None（使用当前目录）
        """
        self.template_dir = template_dir or Path.cwd()

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板（简化版，不支持复杂语法）

        Args:
            template_name: 模板文件名
            context: 模板变量

        Returns:
            str: 渲染后的内容
        """
        # 查找模板文件
        template_path = self._find_template(template_name)
        if not template_path:
            raise TemplateError(f"模板文件不存在: {template_name}")

        # 读取模板内容
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 简单的占位符替换
        result = template_content
        for key, value in context.items():
            # 替换 {{ .Key }} 或 {{ Key }} 格式
            patterns = [
                f"{{ .{key} }}",
                f"{{{key}}}",
                f"{{.{key}}}",
                f"{{ {key} }}"
            ]
            for pattern in patterns:
                result = result.replace(pattern, str(value))

        return result

    def _find_template(self, template_name: str) -> Optional[Path]:
        """
        查找模板文件

        Args:
            template_name: 模板文件名

        Returns:
            Optional[Path]: 模板文件路径，如果不存在返回 None
        """
        # 检查当前模板目录
        candidates = [
            self.template_dir / template_name,
            self.template_dir / f"{template_name}.go.tmpl",
            self.template_dir / f"{template_name}.tmpl",
            self.template_dir / f"{template_name}.md",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # 检查父目录的 templates/common 目录
        common_dir = self.template_dir.parent / "templates" / "common"
        if common_dir.exists():
            for candidate in candidates:
                common_candidate = common_dir / candidate.name
                if common_candidate.exists():
                    return common_candidate

        return None

    def render_to_file(
        self,
        template_name: str,
        output_path: Path,
        context: Dict[str, Any]
    ) -> bool:
        """
        渲染模板并写入文件

        Args:
            template_name: 模板文件名
            output_path: 输出文件路径
            context: 模板变量

        Returns:
            bool: 是否成功
        """
        try:
            content = self.render(template_name, context)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise TemplateError(f"渲染模板到文件失败: {e}")

    @staticmethod
    def render_string(template_string: str, context: Dict[str, Any]) -> str:
        """
        渲染字符串模板

        Args:
            template_string: 模板字符串
            context: 模板变量

        Returns:
            str: 渲染后的内容
        """
        result = template_string
        for key, value in context.items():
            patterns = [
                f"{{ .{key} }}",
                f"{{{key}}}",
                f"{{.{key}}}",
                f"{{ {key} }}"
            ]
            for pattern in patterns:
                result = result.replace(pattern, str(value))

        return result
