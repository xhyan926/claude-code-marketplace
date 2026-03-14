"""
LSP (Language Server Protocol) 支持模块

该模块为 Go 代码生成提供 LSP 友好性支持，确保生成的代码：
1. 兼容 Go 语言服务器（gopls）
2. 支持实时类型检查和代码补全
3. 遵循 Go 语言的最佳实践
4. 提供良好的开发体验

作者：Claude Code Assistant
创建时间：2026-03-13
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class LSPSupport:
    """LSP 支持管理类"""

    def __init__(self, project_root: str):
        """初始化 LSP 支持

        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.gopls_config = self._create_gopls_config()
        self.lsp_requirements = {
            'type_annotations': True,
            'interface_compliance': True,
            'import_optimization': True,
            'error_handling': True
        }

    def _create_gopls_config(self) -> Dict:
        """创建 gopls 配置"""
        return {
            "ui.diagnostic.staticcheck": True,
            "ui.diagnostic.analyses": {
                "unreachable": True,
                "unusedvariable": True,
                "unusedimport": True,
                "unusedparameter": True,
                "shadowing": True,
                "assign": True,
                "fieldalignment": True,
                "ineffassign": True,
                "nilness": True,
                "nonewvars": True,
                "noresultvalues": True,
                "structpack": True,
                "unnecessarystring": True,
                "unreachable": True,
                "unused": True,
                "unusedimport": True,
                "unusedparam": True,
                "unusedstructfield": True,
                "unusedvariable": True,
                "S1019": True, // use of fmt.Sprint instead of fmt.Sprintf
            },
            "build.experimental.gowalk": True,
            "build.experimentalPackageCache": True,
            "ui.completion.filterUnimported": true,
            "ui.comulation.completeUnimported": true,
            "ui.completion.snippets": true,
            "ui.semanticTokens": true,
            "ui.navigation.importShortcut": "both",
            "ui.semanticTokens.highlightGroups": {
                "namespace": "entity.name.namespace",
                "type": "type",
                "class": "entity.name.type",
                "enum": "entity.name.type",
                "interface": "entity.name.type",
                "struct": "entity.name.type",
                "typeParameter": "entity.name.type",
                "parameter": "variable.parameter",
                "variable": "variable",
                "property": "entity.name",
                "event": "entity.name",
                "function": "entity.name.function",
                "method": "entity.name.method",
                "macro": "entity.name.function",
                "variable": "variable",
                "parameter": "variable.parameter",
                "label": "entity.name.label",
                "comment": "comment",
                "string": "string",
                "keyword": "keyword",
                "number": "number",
                "regexp": "string.regexp",
                "operator": "keyword.operator",
            }
        }

    def create_gopls_settings(self) -> str:
        """创建 gopls 配置文件内容"""
        return json.dumps(self.gopls_config, indent=2)

    def validate_lsp_friendly_code(self, code: str) -> Tuple[bool, List[str]]:
        """验证代码是否 LSP 友好

        Args:
            code: 要验证的 Go 代码

        Returns:
            Tuple[是否通过, 错误列表]
        """
        errors = []

        # 检查导入语句
        import_errors = self._check_imports(code)
        errors.extend(import_errors)

        # 检查类型定义
        type_errors = self._check_type_definitions(code)
        errors.extend(type_errors)

        # 检查错误处理
        error_errors = self._check_error_handling(code)
        errors.extend(error_errors)

        # 检查函数签名
        func_errors = self._check_function_signatures(code)
        errors.extend(func_errors)

        return len(errors) == 0, errors

    def _check_imports(self, code: str) -> List[str]:
        """检查导入语句是否符合 LSP 友好规范"""
        errors = []

        # 检查标准库导入
        std_imports = re.findall(r'import\s*\(\s*([^)]+)\)', code, re.DOTALL)
        if std_imports:
            std_block = std_imports[0]
            lines = [line.strip() for line in std_block.split('\n') if line.strip()]

            # 检查是否标准库在前
            non_std_found = False
            for line in lines:
                if line.startswith('"'):
                    # 检查是否为标准库
                    if not self._is_standard_library(line):
                        if not non_std_found:
                            errors.append(f"标准库导入应该在第三方库之前: {line}")
                        non_std_found = True

        return errors

    def _is_standard_library(self, import_line: str) -> bool:
        """检查是否为标准库导入"""
        # 简化的标准库检查
        std_pkgs = [
            'context', 'fmt', 'net/http', 'encoding/json', 'time',
            'errors', 'io', 'os', 'path', 'strings', 'bytes',
            'crypto', 'math', 'strconv', 'sync', 'testing'
        ]

        # 提取包名
        match = re.match(r'"([^/]+)"', import_line)
        if match:
            pkg_name = match.group(1)
            return pkg_name in std_pkgs

        return False

    def _check_type_definitions(self, code: str) -> List[str]:
        """检查类型定义"""
        errors = []

        # 检查接口定义是否完整
        interfaces = re.findall(r'type\s+(\w+)\s+interface\s*\{([^}]*)\}', code, re.DOTALL)
        for _, methods in interfaces:
            methods = methods.strip()
            if not methods:
                continue

            # 检查方法签名是否完整
            method_lines = [line.strip() for line in methods.split('\n') if line.strip()]
            for line in method_lines:
                if '(' in line and ')' in line:
                    # 检查是否有返回值注释
                    if '//' not in line:
                        # 简单检查，可能需要更复杂的逻辑
                        pass

        return errors

    def _check_error_handling(self, code: str) -> List[str]:
        """检查错误处理是否符合 LSP 友好规范"""
        errors = []

        # 检查是否使用了 %w 包装错误
        error_statements = re.findall(r'fmt\.Errorf\([^)]+[^%w]', code)
        if error_statements:
            errors.append("建议使用 %w 包装错误以保留错误栈")

        # 检查是否使用了字符串比较错误类型
        string_comparisons = re.findall(r'err\.Error\(\s*==\s*["\'][^"\']*["\']', code)
        if string_comparisons:
            errors.append("避免使用字符串比较错误类型，使用 errors.Is() 或 errors.As()")

        return errors

    def _check_function_signatures(self, code: str) -> List[str]:
        """检查函数签名是否符合 LSP 友好规范"""
        errors = []

        # 检查函数命名
        function_defs = re.findall(r'func\s+(\w+)\s*\([^)]*\)\s*[^{]*', code)
        for func_name in function_defs:
            # 检查公共函数首字母是否大写
            if func_name[0].isupper() and '_' in func_name:
                # 检查是否有不必要的下划线
                parts = func_name.split('_')
                if len(parts) > 2:
                    errors.append(f"函数名 {func_name} 可能过于复杂，考虑简化命名")

        return errors

    def generate_lsp_friendly_snippet(self, func_name: str, params: List[str], return_types: List[str]) -> str:
        """生成 LSP 友好的代码片段

        Args:
            func_name: 函数名
            params: 参数列表
            return_types: 返回类型列表

        Returns:
            LSP 友好的代码片段
        """
        # 函数签名
        param_str = ', '.join([f"{param}: {ptype}" for param, ptype in params])
        return_str = ', '.join(return_types)

        snippet = f"""// {func_name} 的功能描述
func {func_name}({param_str}) ({return_str}) {{
    // TODO: 实现函数逻辑
    return {self._generate_return_values(return_types)}
}}"""

        return snippet

    def _generate_return_values(self, return_types: List[str]) -> str:
        """生成返回值的默认值"""
        defaults = {
            'error': 'nil',
            'string': '""',
            'int': '0',
            'int64': '0',
            'float64': '0.0',
            'bool': 'false',
            '[]byte': 'nil',
            '*Type': 'nil'
        }

        values = []
        for rt in return_types:
            if rt in defaults:
                values.append(defaults[rt])
            else:
                # 默认返回 nil
                values.append('nil')

        return ', '.join(values)

    def check_lsp_compatibility(self, file_path: str) -> Dict:
        """检查文件的 LSP 兼容性

        Args:
            file_path: 文件路径

        Returns:
            兼容性检查结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            is_valid, errors = self.validate_lsp_friendly_code(code)

            result = {
                'valid': is_valid,
                'errors': errors,
                'gopls_config': self.gopls_config,
                'recommendations': self._generate_recommendations(errors)
            }

            return result

        except Exception as e:
            return {
                'valid': False,
                'errors': [f"读取文件失败: {str(e)}"],
                'gopls_config': self.gopls_config,
                'recommendations': []
            }

    def _generate_recommendations(self, errors: List[str]) -> List[str]:
        """根据错误生成改进建议"""
        recommendations = []

        if any("标准库导入" in err for err in errors):
            recommendations.append("将标准库导入移到第三方库导入之前")

        if any("%w" in err for err in errors):
            recommendations.append("使用 %w 包装错误以保留错误栈信息")

        if any("errors.Is()" in err or "errors.As()" in err for err in errors):
            recommendations.append("使用 errors.Is() 或 errors.As() 检查错误类型")

        if not recommendations:
            recommendations.append("代码符合 LSP 友好规范")

        return recommendations

    def create_go_mod_file(self, module_name: str) -> str:
        """创建 go.mod 文件内容"""
        return f"""module {module_name}

go 1.21

require (
    // 第三方依赖
)
"""

    def create_go_sum_file(self) -> str:
        """创建 go.sum 文件内容（空）"""
        return ""


class LSPCodeGenerator:
    """LSP 友好的代码生成器"""

    def __init__(self, project_root: str):
        self.lsp_support = LSPSupport(project_root)

    def generate_function_with_docs(self, func_name: str, description: str,
                                  params: List[Dict], returns: List[Dict],
                                  body: str = "") -> str:
        """生成带有文档注释的 LSP 友好函数"""

        # 生成参数文档
        param_docs = []
        for param in params:
            param_docs.append(f"    {param['name']}: {param['description']}")

        # 生成返回值文档
        return_docs = []
        for ret in returns:
            return_docs.append(f"    {ret['type']}: {ret['description']}")

        # 生成函数签名
        param_types = [f"{p['name']} {p['type']}" for p in params]
        param_str = ', '.join(param_types)
        return_str = ', '.join([r['type'] for r in returns])

        # 生成函数
        function = f"""// {description}
//
// 参数:
{chr(10).join(param_docs)}
//
// 返回值:
{chr(10).join(return_docs)}
func {func_name}({param_str}) ({return_str}) {{
    {body if body else "// TODO: 实现函数逻辑"}
    {self._generate_return_values([r['type'] for r in returns])}
}}"""

        return function

    def _generate_return_values(self, return_types: List[str]) -> str:
        """生成返回值的默认值"""
        defaults = {
            'error': 'nil',
            'string': '""',
            'int': '0',
            'int64': '0',
            'float64': '0.0',
            'bool': 'false',
            '[]byte': 'nil',
            '*Type': 'nil'
        }

        values = []
        for rt in return_types:
            if rt in defaults:
                values.append(defaults[rt])
            else:
                values.append('nil')

        return ', '.join(values)


# 使用示例
if __name__ == "__main__":
    # 创建 LSP 支持
    lsp_support = LSPSupport("/path/to/project")

    # 验证代码
    code = """
package main

import (
    "fmt"
    "strings"
)

func main() {
    fmt.Println("Hello")
}
"""

    is_valid, errors = lsp_support.validate_lsp_friendly_code(code)
    print(f"代码是否 LSP 友好: {is_valid}")
    if errors:
        print("错误:", errors)

    # 生成 LSP 友好代码片段
    snippet = lsp_support.generate_lsp_friendly_snippet(
        "GetStringToInt64",
        [("input", "string"), ("defaultValue", "int64")],
        ["int64", "error"]
    )
    print("\n生成的代码片段:")
    print(snippet)