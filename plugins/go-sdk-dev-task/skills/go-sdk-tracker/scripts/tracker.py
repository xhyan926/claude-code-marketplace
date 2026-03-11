#!/usr/bin/env python3
"""
任务状态跟踪脚本

使用方法：
    python tracker.py --task-path subtasks/task-01 --status completed
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# 添加 common 模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

from skill_base import SkillBase
from validators import Validator
from error_handler import DependencyError


class TaskTracker(SkillBase):
    """任务跟踪器"""

    def __init__(self):
        super().__init__()
        self.validator = Validator()

    def read_status(self, task_path: Path) -> Optional[str]:
        """读取子任务状态"""
        status_file = task_path / "STATUS"
        if not status_file.exists():
            return None

        with open(status_file, 'r') as f:
            return f.read().strip()

    def write_status(self, task_path: Path, status: str) -> None:
        """写入子任务状态"""
        status_file = task_path / "STATUS"
        with open(status_file, 'w') as f:
            f.write(status + '\n')

    def verify_files(self, task_path: Path) -> bool:
        """验证子任务关键文件是否存在"""
        required_files = ["TASK.md", "IMPLEMENTATION.md", "TEST_PLAN.md"]
        for filename in required_files:
            if not (task_path / filename).exists():
                self.logger.warning(f"缺少必需文件 {filename}")
                return False
        return True

    def check_dependencies(self, task_path: Path) -> bool:
        """检查依赖的前置任务是否已完成"""
        task_file = task_path / "TASK.md"
        if not task_file.exists():
            return True

        # 读取任务文件，查找依赖信息
        with open(task_file, 'r') as f:
            content = f.read()

        # 查找前置子任务
        if "前置子任务" in content or "prerequisites" in content.lower():
            # 解析依赖的任务 ID
            import re
            matches = re.findall(r'task-\d+', content)
            for match in matches:
                dep_path = task_path.parent / match
                if dep_path.exists():
                    dep_status = self.read_status(dep_path)
                    if dep_status != "completed":
                        self.logger.error(
                            f"前置任务 {match} 未完成（状态: {dep_status}）"
                        )
                        return False

        return True

    def update_subtasks_md(self, subtasks_md: Path, task_id: str, status: str) -> None:
        """更新 SUBTASKS.md 中的任务状态"""
        if not subtasks_md.exists():
            self.logger.warning("SUBTASKS.md 不存在，跳过更新")
            return

        with open(subtasks_md, 'r') as f:
            lines = f.readlines()

        updated_lines = []
        for i, line in enumerate(lines):
            # 查找对应的子任务行并更新状态
            if f"- [ ] 子任务 {task_id[5:]}" in line or \
               f"- [ ] task-{task_id[5:]}" in line:
                if status == "completed":
                    lines[i] = line.replace("- [ ]", "- [x]")
                elif status in ["pending", "in_progress"]:
                    lines[i] = line.replace("- [x]", "- [ ]")
                break

        with open(subtasks_md, 'w') as f:
            f.writelines(lines)

    def validate_status(self, status: str) -> bool:
        """验证状态值"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'blocked']
        return status in valid_statuses

    def execute(self, context: dict) -> dict:
        """执行状态更新"""
        task_path = Path(context['task_path'])
        status = context['status']
        force = context.get('force', False)

        # 验证路径存在
        if not task_path.exists():
            raise ValueError(f"子任务路径 {task_path} 不存在")

        # 验证状态值
        if not self.validate_status(status):
            raise ValueError(
                f"无效的状态值: {status}，"
                f"必须是以下值之一: pending, in_progress, completed, blocked"
            )

        # 读取当前状态
        current_status = self.read_status(task_path)
        self.logger.info(f"当前状态：{current_status if current_status else '未设置'}")
        self.logger.info(f"目标状态：{status}")

        # 验证步骤（非强制模式）
        if not force and status == "completed":
            # 检查必需文件
            if not self.verify_files(task_path):
                raise ValueError("缺少必需文件，无法标记为完成（使用 --force 跳过）")

            # 检查依赖
            if not self.check_dependencies(task_path):
                raise DependencyError(
                    "依赖的前置任务未完成（使用 --force 跳过）",
                    required_tasks=self._get_prerequisites(task_path)
                )

        # 更新状态
        self.write_status(task_path, status)
        self.logger.info(f"✓ 状态已更新为：{status}")

        # 更新 SUBTASKS.md
        subtasks_md = task_path.parent.parent / "SUBTASKS.md"
        task_id = task_path.name
        self.update_subtasks_md(subtasks_md, task_id, status)
        self.logger.info(f"✓ SUBTASKS.md 已更新")

        return {
            "status": "success",
            "task_path": str(task_path),
            "old_status": current_status,
            "new_status": status
        }

    def _get_prerequisites(self, task_path: Path) -> list:
        """获取前置任务列表"""
        task_file = task_path / "TASK.md"
        if not task_file.exists():
            return []

        with open(task_file, 'r') as f:
            content = f.read()

        import re
        matches = re.findall(r'task-\d+', content)
        return matches


def main():
    parser = argparse.ArgumentParser(description='更新子任务状态')
    parser.add_argument('--task-path', required=True, help='子任务路径（如 subtasks/task-01）')
    parser.add_argument('--status', required=True,
                        choices=['pending', 'in_progress', 'completed', 'blocked'],
                        help='要设置的状态')
    parser.add_argument('--force', action='store_true', help='强制更新，跳过验证')

    args = parser.parse_args()

    tracker = TaskTracker()

    try:
        result = tracker.execute({
            'task_path': args.task_path,
            'status': args.status,
            'force': args.force
        })
        print(f"✓ 成功：{result['new_status']}")
    except Exception as e:
        print(f"✗ 失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
