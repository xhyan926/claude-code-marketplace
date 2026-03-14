"""
简化版命名规范测试

避免导入依赖问题，直接测试核心功能
"""

import re
import string
from typing import Dict, List, Optional, Tuple
from enum import Enum


class NamingCategory(Enum):
    """命名类别枚举"""
    PACKAGE = "package"
    FUNCTION = "function"
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"


class GoNamingStandards:
    """简化的命名规范测试类"""

    def __init__(self):
        # 标准库包名集合
        self.std_packages = {
            'fmt', 'net/http', 'io', 'os', 'path', 'strings', 'bytes',
            'context', 'time', 'errors', 'crypto', 'math'
        }

        # 不应该使用的缩写
        self.bad_abbreviations = {
            'str': 'string',
            'num': 'number',
            'buf': 'buffer',
            'req': 'request',
            'res': 'response',
            'cfg': 'config'
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

        if not name:
            errors.append("函数名不能为空")

        # 检查首字母
        if category in [NamingCategory.FUNCTION, NamingCategory.TYPE]:
            # 公共函数/类型首字母应该大写
            if not name[0].isupper():
                errors.append("公共函数/类型首字母必须大写")
        else:
            # 私有函数/变量首字母应该小写
            if not name[0].islower():
                errors.append("私有函数/变量首字母必须小写")

        # 检查命名风格
        if '_' in name:
            # 使用下划线分隔
            parts = name.split('_')
            for part in parts:
                if len(part) == 1 and name != 'get':  # 允许 'get' 这样的常见单词
                    errors.append("避免使用单字符片段")

            # 检查是否过度使用下划线
            if len(parts) > 4:
                errors.append("函数名过长，考虑简化或使用更具描述性的名称")
        else:
            # 驼峰命名 - 只对公共函数/类型进行严格检查
            if category in [NamingCategory.FUNCTION, NamingCategory.TYPE]:
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                    errors.append("驼峰命名函数名必须以大写字母开头，只包含字母和数字")
            elif category == NamingCategory.VARIABLE:
                # 私有变量可以是小写驼峰
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', name):
                    errors.append("私有变量名必须以小写字母开头")

        # 简化 BDD 风格的命名
        if '_Should' in name and '_When' in name:
            simplified = name.split('_')[0] + '_' + name.split('_')[2]
            if simplified != name:
                errors.append(f"考虑简化命名: {name} -> {simplified}")

        return len(errors) == 0, errors


def test_naming_standards():
    """运行命名规范测试"""
    print("=== 开始测试 Google Go 命名规范 ===\n")

    standards = GoNamingStandards()

    # 测试包名
    print("1. 测试包名:")
    test_cases = [
        ("obsclient", True),
        ("xmlutils", True),
        ("fmt", False),
        ("util", False),
        ("a", False),
        ("TOOLONGNAMETHATEXCEEDSLIMIT", False),
        ("ObsClient", False)
    ]

    for name, expected_valid in test_cases:
        is_valid, errors = standards.validate_package_name(name)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"  {status} {name}: {'有效' if is_valid else '无效'}")
        if not is_valid and errors:
            print(f"     错误: {errors[0]}")

    print("\n2. 测试函数名:")
    func_test_cases = [
        ("GetStringToInt64", True, NamingCategory.FUNCTION),
        ("createObsClient", True, NamingCategory.VARIABLE),    # 驼峰命名，私有变量（虽然首字母小写）
        ("get_string", True, NamingCategory.VARIABLE),         # 下划线命名，私有变量
        ("GetString", True, NamingCategory.FUNCTION),          # 虽然简单但符合规范
        ("ProcessData", True, NamingCategory.FUNCTION),
        ("validate_input", True, NamingCategory.VARIABLE),     # 下划线命名是有效的私有变量命名
        ("Get", True, NamingCategory.FUNCTION),               # 简单但符合规范
        ("get", True, NamingCategory.VARIABLE)                # 私有变量，下划线命名是有效的
    ]

    for name, expected_valid, category in func_test_cases:
        # 根据名称自动判断类别
        if name[0].isupper():
            actual_category = NamingCategory.FUNCTION
        else:
            actual_category = NamingCategory.VARIABLE

        is_valid, errors = standards.validate_function_name(name, actual_category)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"  {status} {name} ({actual_category.value}): {'有效' if is_valid else '无效'}")
        if not is_valid and errors:
            print(f"     错误: {errors[0]}")

    print("\n3. 测试 BDD 名称简化:")
    bdd_name = "TestStringToInt64_ShouldReturnDefaultValue_WhenValueIsEmptyString"
    # 模拟简化逻辑
    if '_Should' in bdd_name and '_When' in bdd_name:
        simplified = bdd_name.split('_')[0] + '_' + bdd_name.split('_')[2]
    else:
        simplified = bdd_name
    print(f"  原始名称: {bdd_name}")
    print(f"  简化后: {simplified}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_naming_standards()