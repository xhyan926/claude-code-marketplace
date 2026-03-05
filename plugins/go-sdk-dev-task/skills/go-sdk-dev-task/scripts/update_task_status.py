#!/usr/bin/env python3
"""
更新子任务状态的脚本

使用方法：
    python update_task_status.py --task-path subtasks/task-01 --status completed
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional


def read_status(task_path: Path) -> Optional[str]:
    """读取子任务状态"""
    status_file = task_path / "STATUS"
    if not status_file.exists():
        return None

    with open(status_file, 'r') as f:
        return f.read().strip()


def write_status(task_path: Path, status: str) -> None:
    """写入子任务状态"""
    status_file = task_path / "STATUS"
    with open(status_file, 'w') as f:
        f.write(status + '\n')


def verify_files(task_path: Path) -> bool:
    """验证子任务关键文件是否存在"""
    required_files = ["TASK.md", "IMPLEMENTATION.md", "TEST_PLAN.md"]
    for filename in required_files:
        if not (task_path / filename).exists():
            print(f"警告：缺少必需文件 {filename}")
            return False
    return True


def check_dependencies(task_path: Path) -> bool:
    """检查依赖的前置任务是否已完成"""
    task_file = task_path / "TASK.md"
    if not task_file.exists():
        return True

    # 读取任务文件，查找依赖信息
    with open(task_file, 'r') as f:
        content = f.read()

    # 简单实现：检查是否有明确的依赖标记
    # 实际使用时可以扩展为更复杂的依赖解析
    if "前置子任务" in content:
        # 这里可以添加更复杂的依赖检查逻辑
        pass

    return True


def update_subtasks_md(subtasks_md: Path, task_id: str, status: str) -> None:
    """更新 SUBTASKS.md 中的任务状态"""
    if not subtasks_md.exists():
        print("SUBTASKS.md 不存在，跳过更新")
        return

    with open(subtasks_md, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    for i, line in enumerate(lines):
        # 查找对应的子任务行并更新状态
        if f"- [ ] 子任务 {task_id[5:]}" in line:
            if status == "completed":
                lines[i] = line.replace("- [ ]", "- [x]")
            elif status in ["pending", "in_progress"]:
                lines[i] = line.replace("- [x]", "- [ ]")
            break

    with open(subtasks_md, 'w') as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(description='更新子任务状态')
    parser.add_argument('--task-path', required=True, help='子任务路径（如 subtasks/task-01）')
    parser.add_argument('--status', required=True, choices=['pending', 'in_progress', 'completed'],
                        help='要设置的状态')
    parser.add_argument('--force', action='store_true', help='强制更新，跳过验证')

    args = parser.parse_args()

    task_path = Path(args.task_path)

    # 验证路径存在
    if not task_path.exists():
        print(f"错误：子任务路径 {task_path} 不存在")
        sys.exit(1)

    # 读取当前状态
    current_status = read_status(task_path)
    print(f"当前状态：{current_status if current_status else '未设置'}")
    print(f"目标状态：{args.status}")

    # 验证步骤（非强制模式）
    if not args.force:
        if args.status == "completed":
            # 检查必需文件
            if not verify_files(task_path):
                print("错误：缺少必需文件，无法标记为完成")
                print("使用 --force 参数可以跳过此检查")
                sys.exit(1)

            # 检查依赖
            if not check_dependencies(task_path):
                print("错误：依赖的前置任务未完成")
                sys.exit(1)

    # 更新状态
    write_status(task_path, args.status)
    print(f"✓ 状态已更新为：{args.status}")

    # 更新 SUBTASKS.md
    subtasks_md = task_path.parent.parent / "SUBTASKS.md"
    task_id = task_path.name
    update_subtasks_md(subtasks_md, task_id, args.status)
    print(f"✓ SUBTASKS.md 已更新")


if __name__ == "__main__":
    main()
