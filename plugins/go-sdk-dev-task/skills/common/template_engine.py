"""
模板引擎

支持 Go template 语法的模板渲染（使用 jinja2 实现）。
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json


class TemplateError(Exception):
    """模板错误"""
    pass


class TemplateEngine:
    """模板引擎"""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        初始化模板引擎

        Args:
            template_dir: 模板目录路径，默认为 None（使用当前目录）
        """
        self.template_dir = template_dir or Path.cwd()
        self.env = self._create_environment()

    def _create_environment(self):
        """创建 Jinja2 环境"""
        try:
            import jinja2
        except ImportError:
            raise TemplateError(
                "jinja2 未安装，请运行: pip install jinja2"
            )

        if self.template_dir.exists():
            loader = jinja2.FileSystemLoader(str(self.template_dir))
        else:
            # 如果模板目录不存在，使用空加载器
            loader = jinja2.FileSystemLoader(".")

        env = jinja2.Environment(
            loader=loader,
            undefined=jinja2.StrictUndefined,  # 严格模式，未定义的变量会报错
            trim_blocks=True,  # 去除行尾空白
            lstrip_blocks=True,  # 去除行首空白
            keep_trailing_newline=True,  # 保留尾部换行符
        )

        # 注册自定义过滤器
        env.filters.update({
            'snake_case': self._snake_case,
            'camel_case': self._camel_case,
            'pascal_case': self._pascal_case,
            'kebab_case': self._kebab_case,
        })

        return env

    def _snake_case(self, text: str) -> str:
        """转换为 snake_case"""
        import re
        text = re.sub('([A-Z])', r'_\1', text).lower().lstrip('_')
        return text

    def _camel_case(self, text: str) -> str:
        """转换为 camelCase"""
        words = text.replace('_', ' ').split()
        if not words:
            return text
        return words[0].lower() + ''.join(w.capitalize() for w in words[1:])

    def _pascal_case(self, text: str) -> str:
        """转换为 PascalCase"""
        return ''.join(w.capitalize() for w in text.replace('_', ' ').split())

    def _kebab_case(self, text: str) -> str:
        """转换为 kebab-case"""
        import re
        return re.sub('([A-Z])', r'-\1', text).lower().lstrip('-')

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板

        Args:
            template_name: 模板文件名（支持 .go.tmpl 后缀）
            context: 模板变量

        Returns:
            str: 渲染后的内容

        Raises:
            TemplateError: 模板渲染失败
        """
        try:
            # 查找模板文件
            template_path = self._find_template(template_name)
            if not template_path:
                raise TemplateError(f"模板文件不存在: {template_name}")

            # 读取模板内容
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 转换 Go template 语法为 Jinja2 语法
            template_content = self._convert_go_template(template_content)

            # 创建并渲染模板
            template = self.env.from_string(template_content)
            result = template.render(context)

            return result

        except Exception as e:
            import jinja2
            if isinstance(e, jinja2.TemplateSyntaxError):
                raise TemplateError(f"模板语法错误: {e}")
            raise TemplateError(f"模板渲染失败: {e}")

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

    def _convert_go_template(self, content: str) -> str:
        """
        转换 Go template 语法为 Jinja2 语法

        Args:
            content: Go template 内容

        Returns:
            str: Jinja2 兼容的内容
        """
        try:
            import jinja2
        except ImportError:
            raise TemplateError("jinja2 未安装")

        # Go template 语法映射
        # 转换控制结构
        content = content.replace('{{ if ', '{% if ')
        content = content.replace('{{ end }}', '{% endif %}')
        content = content.replace('{{ range ', '{% for ')

        # 转换变量引用（去掉点表示法）
        content = content.replace('{{ .', '{{ ')

        return content

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        渲染字符串模板

        Args:
            template_string: 模板字符串
            context: 模板变量

        Returns:
            str: 渲染后的内容
        """
        try:
            import jinja2
        except ImportError:
            raise TemplateError("jinja2 未安装")

        try:
            template = self.env.from_string(template_string)
            return template.render(context)
        except Exception as e:
            raise TemplateError(f"字符串模板渲染失败: {e}")

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
    def from_string(template_string: str):
        """
        从字符串创建模板

        Args:
            template_string: 模板字符串

        Returns:
            Template: Jinja2 模板对象
        """
        try:
            import jinja2
        except ImportError:
            raise TemplateError("jinja2 未安装")

        env = jinja2.Environment(
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        return env.from_string(template_string)
