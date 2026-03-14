"""
Go 命名规范模块

该模块实现了 Google Go Style Guide 的命名规范，确保生成的代码：
1. 符合 Google 推荐的命名约定
2. 具有良好的可读性和一致性
3. LSP 友好的命名方式
4. 避免常见的命名陷阱

作者：Claude Code Assistant
创建时间：2026-03-13
"""

import re
import string
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum


class NamingCategory(Enum):
    """命名类别枚举"""
    PACKAGE = "package"
    FUNCTION = "function"
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    INTERFACE = "interface"
    STRUCT = "struct"
    METHOD = "method"


class GoNamingStandards:
    """Go 命名规范管理类"""

    def __init__(self):
        # 标准库包名集合
        self.std_packages = {
            'context', 'fmt', 'net/http', 'encoding/json', 'time',
            'errors', 'io', 'os', 'path', 'strings', 'bytes',
            'crypto', 'math', 'strconv', 'sync', 'testing',
            'encoding', 'reflect', 'unsafe', 'syscall', 'flag',
            'log', 'html', 'url', 'regexp', 'unicode',
            'container/list', 'container/ring', 'sort',
            'compress/gzip', 'compress/flate', 'compress/lzw',
            'database/sql', 'database/sql/driver', 'text/template',
        }

        # 常见的不应该使用的缩写
        self.bad_abbreviations = {
            'str': 'string',
            'num': 'number',
            'buf': 'buffer',
            'req': 'request',
            'res': 'response',
            'cfg': 'config',
            'env': 'environment',
            'tmp': 'temporary',
            'err': 'error',  # 只有用于 error 类型变量时可用
            'val': 'value',
            'obj': 'object',
            'data': 'data',  // 只有当没有更好的描述性名称时才使用
        }

        # 需要大写的特殊单词
        self.caps_words = {
            'ID', 'UUID', 'JSON', 'XML', 'YAML', 'SQL', 'HTTP',
            'HTTPS', 'URL', 'URI', 'TCP', 'UDP', 'IP', 'EOF',
            'GOPATH', 'GOROOT', 'GOPROXY', 'GOSUMDB'
        }

    def validate_package_name(self, name: str) -> Tuple[bool, List[str]]:
        """验证包名是否符合 Google 规范"""
        errors = []

        # 检查包名长度
        if len(name) < 2:
            errors.append("包名至少需要 2 个字符")

        if len(name) > 20:
            errors.append("包名不应超过 20 个字符")

        # 检查字符格式
        if not name.islower():
            errors.append("包名必须全部小写")

        if name.replace('_', '').isalnum():
            # 包名应该包含有意义的名称，不仅仅是数字
            if name.isdigit():
                errors.append("包名不能仅为数字")
        else:
            errors.append("包名只能包含字母、数字和下划线")

        # 检查是否为标准库名
        if name in self.std_packages:
            errors.append(f"包名 '{name}' 与标准库名冲突")

        # 检查是否使用缩写
        if name in self.bad_abbreviations:
            suggestion = self.bad_abbreviations[name]
            errors.append(f"避免使用缩写 '{name}'，建议使用 '{suggestion}'")

        # 检查常见的不规范包名
        bad_names = {'sdk', 'lib', 'util', 'common', 'base', 'core'}
        if name in bad_names:
            errors.append(f"避免使用通用名称 '{name}'，请使用更具体的名称")

        return len(errors) == 0, errors

    def validate_function_name(self, name: str, category: NamingCategory = NamingCategory.FUNCTION) -> Tuple[bool, List[str]]:
        """验证函数名是否符合 Google 规范"""
        errors = []

        # 检查基本格式
        if not name:
            errors.append("函数名不能为空")

        # 检查首字母
        if category in [NamingCategory.FUNCTION, NamingCategory.METHOD, NamingCategory.TYPE]:
            # 公共函数/方法/类型首字母应该大写
            if not name[0].isupper():
                errors.append("公共函数/方法/类型首字母必须大写")
        else:
            # 私有函数/变量首字母应该小写
            if not name[0].islower():
                errors.append("私有函数/变量首字母必须小写")

        # 检查命名风格
        if '_' in name:
            # 使用下划线分隔
            parts = name.split('_')
            for part in parts:
                if len(part) == 1:
                    errors.append("避免使用单字符片段")
                if not part.isalnum():
                    errors.append("函数名只能包含字母、数字和下划线")

            # 检查是否过度使用下划线
            if len(parts) > 4:
                errors.append("函数名过长，考虑简化或使用更具描述性的名称")
        else:
            # 驼峰命名
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                errors.append("驼峰命名函数名必须以大写字母开头，只包含字母和数字")

        # 检查常见的不规范命名
        bad_names = {'Do', 'Get', 'Set', 'Handle', 'Process', 'Run', 'Exec'}
        if name in bad_names:
            errors.append(f"避免使用过于通用的函数名 '{name}'，请使用更具描述性的名称")

        # 检查缩写使用
        for bad_abbr in self.bad_abbreviations:
            if bad_abbr in name.lower():
                suggestion = self.bad_abbreviations[bad_abbr]
                errors.append(f"避免使用缩写 '{bad_abbr}'，建议使用 '{suggestion}'")

        # 简化后的命名建议（替代复杂的 BDD 命名）
        if category == NamingCategory.FUNCTION:
            simplified = self.simplify_bdd_name(name)
            if simplified != name:
                errors.append(f"考虑简化命名: {name} -> {simplified}")

        return len(errors) == 0, errors

    def simplify_bdd_name(self, name: str) -> str:
        """简化 BDD 风格的函数名"""
        if '_Should' in name and '_When' in name:
            # TestFunctionName_ShouldResult_WhenCondition_GivenPrecondition
            # 简化为 TestFunctionName_Result
            parts = name.split('_')
            if len(parts) >= 3:
                # 保留函数名和第一个描述词
                return f"{parts[0]}_{parts[2]}"
        return name

    def validate_variable_name(self, name: str) -> Tuple[bool, List[str]]:
        """验证变量名是否符合 Google 规范"""
        return self.validate_function_name(name, NamingCategory.VARIABLE)

    def validate_constant_name(self, name: str) -> Tuple[bool, List[str]]:
        """验证常量名是否符合 Google 规范"""
        errors = []

        if not name:
            errors.append("常量名不能为空")

        # 常量必须全大写，使用下划线分隔
        if not name.isupper():
            errors.append("常量名必须全大写")

        if '_' not in name:
            errors.append("常量名必须使用下划线分隔单词")

        # 检查是否包含无意义的单词
        if name.startswith('THE_'):
            errors.append("避免在常量名中使用 'THE'")

        parts = name.split('_')
        for part in parts:
            if len(part) == 1:
                errors.append("避免使用单字符片段")

        return len(errors) == 0, errors

    def validate_type_name(self, name: str) -> Tuple[bool, List[str]]:
        """验证类型名是否符合 Google 规范"""
        return self.validate_function_name(name, NamingCategory.TYPE)

    def generate_suggested_names(self, base_name: str, category: NamingCategory, purpose: str = "") -> List[str]:
        """生成符合规范的命名建议"""
        suggestions = []

        if category == NamingCategory.PACKAGE:
            # 包名生成
            base = base_name.lower()
            suggestions.extend([
                base,
                base.rstrip('s'),  # 移除复数
                base + 'util',     # 如果是工具包
                base + 'client',    # 如果是客户端
                base + 'service',   # 如果是服务
            ])
        elif category == NamingCategory.FUNCTION:
            # 函数名生成
            if purpose:
                # 根据功能生成
                if 'get' in purpose.lower():
                    suggestions.append(f"Get{base_name}")
                    suggestions.append(f"Fetch{base_name}")
                    suggestions.append(f"Retrieve{base_name}")
                elif 'create' in purpose.lower():
                    suggestions.append(f"Create{base_name}")
                    suggestions.append(f"New{base_name}")
                    suggestions.append(f"Build{base_name}")
                elif 'delete' in purpose.lower():
                    suggestions.append(f"Delete{base_name}")
                    suggestions.append(f"Remove{base_name}")
                elif 'update' in purpose.lower():
                    suggestions.append(f"Update{base_name}")
                    suggestions.append(f"Modify{base_name}")
            else:
                # 简化后的命名
                suggestions.extend([
                    base_name,
                    f"Get{base_name}",
                    f"Create{base_name}",
                    f"Process{base_name}",
                ])
        elif category == NamingCategory.VARIABLE:
            # 变量名生成
            suggestions.extend([
                base_name,
                base_name + 'Str',
                base_name + 'Int',
                base_name + 'List',
                base_name + 'Map',
            ])

        # 过滤掉无效的建议
        valid_suggestions = []
        for suggestion in suggestions:
            is_valid, _ = self.validate_function_name(suggestion, category)
            if is_valid:
                valid_suggestions.append(suggestion)

        return valid_suggestions[:5]  # 返回前 5 个建议

    def normalize_casing(self, name: str, category: NamingCategory) -> str:
        """规范化名称的大小写"""
        if category == NamingCategory.PACKAGE:
            return name.lower()
        elif category == NamingCategory.CONSTANT:
            return name.upper()
        elif category in [NamingCategory.FUNCTION, NamingCategory.TYPE, NamingCategory.METHOD, NamingCategory.INTERFACE, NamingCategory.STRUCT]:
            # 驼峰命名，首字母大写
            return name.capitalize()
        else:
            # 驼峰命名，首字母小写
            return name[0].lower() + name[1:] if name else name

    def check_name_collision(self, name: str, existing_names: Set[str], category: NamingCategory) -> Tuple[bool, List[str]]:
        """检查名称冲突"""
        errors = []

        # 标准化名称进行比较
        normalized = self.normalize_casing(name, category)

        # 检查与现有名称的冲突
        for existing in existing_names:
            if normalized.lower() == existing.lower():
                errors.append(f"名称 '{name}' 与现有名称 '{existing}' 冲突")

        # 检查与标准库的冲突
        if category == NamingCategory.PACKAGE and name in self.std_packages:
            errors.append(f"包名 '{name}' 与标准库名冲突")

        # 检查与常见类型的冲突
        if category == NamingCategory.TYPE and name in ['Error', 'String', 'Int', 'Float', 'Bool', 'Interface']:
            errors.append(f"类型名 '{name}' 与标准类型冲突")

        return len(errors) == 0, errors


class NamingValidator:
    """命名验证器，用于批量验证命名规范"""

    def __init__(self):
        self.standards = GoNamingStandards()

    def validate_file_names(self, file_paths: List[str]) -> Dict[str, Dict]:
        """验证文件名"""
        results = {}

        for file_path in file_paths:
            file_name = file_path.split('/')[-1]
            # 去除扩展名
            if '.' in file_name:
                base_name = file_name.split('.')[0]
            else:
                base_name = file_name

            # 判断文件类型
            if base_name.endswith('_test'):
                category = NamingCategory.FUNCTION
                base_name = base_name[:-5]  # 去掉 _test
            elif base_name.endswith('_internal_test'):
                category = NamingCategory.FUNCTION
                base_name = base_name[:-13]  # 去掉 _internal_test
            elif 'test' in file_name.lower():
                category = NamingCategory.FUNCTION
            else:
                # 假设是源文件
                category = NamingCategory.PACKAGE

            is_valid, errors = self.standards.validate_function_name(base_name, category)
            results[file_path] = {
                'valid': is_valid,
                'errors': errors,
                'category': category.value,
                'suggestions': self.standards.generate_suggested_names(base_name, category) if not is_valid else []
            }

        return results

    def validate_code_names(self, code: str) -> Dict[str, Dict]:
        """验证代码中的命名"""
        results = {}

        # 查找函数定义
        function_pattern = r'func\s+([A-Za-z0-9_]+)\s*\('
        matches = re.findall(function_pattern, code)

        for func_name in matches:
            is_valid, errors = self.standards.validate_function_name(func_name)
            results[func_name] = {
                'valid': is_valid,
                'errors': errors,
                'category': 'function',
                'suggestions': self.standards.generate_suggested_names(func_name, NamingCategory.FUNCTION) if not is_valid else []
            }

        # 查找类型定义
        type_pattern = r'type\s+([A-Z][A-Za-z0-9_]*)\s+(?:struct|interface|func)'
        matches = re.findall(type_pattern, code)

        for type_name in matches:
            is_valid, errors = self.standards.validate_type_name(type_name)
            results[type_name] = {
                'valid': is_valid,
                'errors': errors,
                'category': 'type',
                'suggestions': self.standards.generate_suggested_names(type_name, NamingCategory.TYPE) if not is_valid else []
            }

        return results


# 使用示例
if __name__ == "__main__":
    validator = NamingValidator()

    # 验证包名
    is_valid, errors = validator.standards.validate_package_name("obsclient")
    print(f"包名 'obsclient' 是否有效: {is_valid}")
    if errors:
        print("错误:", errors)

    # 验证函数名
    is_valid, errors = validator.standards.validate_function_name("GetStringToInt64")
    print(f"函数名 'GetStringToInt64' 是否有效: {is_valid}")
    if errors:
        print("错误:", errors)

    # 生成命名建议
    suggestions = validator.standards.generate_suggested_names("Data", NamingCategory.FUNCTION, "get data")
    print("命名建议:", suggestions)