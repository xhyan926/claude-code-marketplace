"""
进度追踪模块

提供进度追踪和 ETA 计算功能。
"""

import time
from typing import Optional
from .logger import get_logger


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, total_steps: int, task_name: str = "任务"):
        """
        初始化进度追踪器

        Args:
            total_steps: 总步骤数
            task_name: 任务名称
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.task_name = task_name
        self.logger = get_logger(f"ProgressTracker[{task_name}]")
        self.step_times = []

    def update(self, step_name: str, status: str = "in_progress") -> None:
        """
        更新进度

        Args:
            step_name: 步骤名称
            status: 状态（in_progress, completed, failed）
        """
        self.current_step += 1
        elapsed = time.time() - self.start_time

        # 计算预计剩余时间
        if self.current_step > 1:
            avg_time_per_step = elapsed / self.current_step
            remaining_steps = self.total_steps - self.current_step
            eta = avg_time_per_step * remaining_steps
        else:
            eta = 0

        # 记录进度
        progress_percent = (self.current_step / self.total_steps) * 100

        status_icon = {
            "in_progress": "⏳",
            "completed": "✓",
            "failed": "✗"
        }.get(status, "?")

        self.logger.info(
            f"[{self.current_step}/{self.total_steps}] "
            f"{status_icon} {step_name} - {status}"
        )
        self.logger.info(
            f"  进度: {progress_percent:.1f}%, "
            f"耗时: {elapsed:.1f}s, "
            f"预计剩余: {eta:.1f}s"
        )

        # 记录步骤完成时间
        if status in ["completed", "failed"]:
            self.step_times.append({
                "step": step_name,
                "time": elapsed
            })

    def complete(self) -> None:
        """标记任务完成"""
        elapsed = time.time() - self.start_time

        self.logger.info(f"✓ {self.task_name} 完成！")
        self.logger.info(f"总耗时: {elapsed:.1f}s")
        self.logger.info(f"平均每步耗时: {elapsed / self.total_steps:.1f}s")

        # 显示步骤耗时统计
        if self.step_times:
            self._show_step_statistics()

    def _show_step_statistics(self) -> None:
        """显示步骤耗时统计"""
        total_time = sum(s["time"] for s in self.step_times)
        avg_time = total_time / len(self.step_times)
        sorted_times = sorted([s["time"] for s in self.step_times])

        self.logger.info("=== 步骤耗时统计 ===")
        self.logger.info(f"最短: {sorted_times[0]:.1f}s")
        self.logger.info(f"最长: {sorted_times[-1]:.1f}s")
        self.logger.info(f"平均: {avg_time:.1f}s")

    def fail(self, error_message: str) -> None:
        """标记任务失败"""
        elapsed = time.time() - self.start_time

        self.logger.error(f"✗ {self.task_name} 失败！")
        self.logger.error(f"错误: {error_message}")
        self.logger.error(f"耗时: {elapsed:.1f}s")
