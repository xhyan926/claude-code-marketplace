"""
交互式问答模块

提供交互式命令行输入功能。
"""

from typing import List, Optional, Any
from .logger import get_logger


class InteractivePrompt:
    """交互式提示器"""

    def __init__(self):
        """初始化交互式提示器"""
        self.logger = get_logger("InteractivePrompt")

    @staticmethod
    def ask_yes_no(question: str, default: bool = True) -> bool:
        """
        提问是否

        Args:
            question: 问题文本
            default: 默认答案

        Returns:
            bool: 用户回答
        """
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} [{default_str}]: ").strip()

        if not response:
            return default

        return response.lower() in ['y', 'yes']

    @staticmethod
    def ask_choice(question: str, options: List[str], default: int = 0) -> str:
        """
        提问选择

        Args:
            question: 问题文本
            options: 选项列表
            default: 默认选项索引

        Returns:
            str: 用户选择的选项
        """
        print(question)
        for i, opt in enumerate(options):
            marker = "> " if i == default else "  "
            print(f"{marker}{i}. {opt}")

        response = input(
            f"选择 [0-{len(options)-1}] [默认: {default}]: "
        ).strip()

        if not response:
            return options[default]

        try:
            index = int(response)
            if 0 <= index < len(options):
                return options[index]
        except ValueError:
            pass

        # 如果输入无效，询问是否重试
        if InteractivePrompt.ask_yes_no("输入无效，是否重试？"):
            return InteractivePrompt.ask_choice(question, options, default)

        return options[default]

    @staticmethod
    def ask_input(
        question: str,
        default: Optional[str] = None,
        password: bool = False
    ) -> str:
        """
        提问输入

        Args:
            question: 问题文本
            default: 默认值
            password: 是否是密码输入

        Returns:
            str: 用户输入
        """
        prompt = question
        if default is not None:
            prompt += f" [默认: {default}]"

        if password:
            import getpass
            response = getpass.getpass(prompt + ": ")
        else:
            response = input(prompt + ": ").strip()

        return response or default

    @staticmethod
    def ask_multiline(question: str) -> str:
        """
        提问多行输入

        Args:
            question: 问题文本

        Returns:
            str: 用户输入的多行文本
        """
        print(f"{question} (输入空行结束):")
        lines = []
        while True:
            line = input("> ")
            if not line:
                break
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def confirm_action(action: str, details: Optional[str] = None) -> bool:
        """
        确认操作

        Args:
            action: 操作描述
            details: 操作详情

        Returns:
            bool: 用户是否确认
        """
        message = f"确认执行以下操作: {action}"
        if details:
            message += f"\n  {details}"

        return InteractivePrompt.ask_yes_no(message)

    @staticmethod
    def select_from_list(
        items: List[Any],
        item_type: str = "项目",
        display_func: Optional[callable] = None
    ) -> Optional[Any]:
        """
        从列表中选择

        Args:
            items: 项目列表
            item_type: 项目类型名称
            display_func: 显示函数

        Returns:
            Optional[Any]: 选中的项目
        """
        if not items:
            print(f"没有可用的 {item_type}")
            return None

        if len(items) == 1:
            return items[0]

        print(f"请选择 {item_type}:")
        for i, item in enumerate(items):
            if display_func:
                display_text = display_func(item)
            else:
                display_text = str(item)

            print(f"  {i}. {display_text}")

        choice = input(f"选择 [0-{len(items)-1}]: ").strip()

        try:
            index = int(choice)
            if 0 <= index < len(items):
                return items[index]
        except ValueError:
            pass

        print("无效的选择")
        return None
