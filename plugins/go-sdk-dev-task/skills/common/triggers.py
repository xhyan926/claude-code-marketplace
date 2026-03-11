"""
技能触发机制

基于上下文检测推荐相关技能。
"""

from typing import List, Dict, Any
from .logger import get_logger
from .context_detector import ContextDetector


class SkillTrigger:
    """技能触发器"""

    def __init__(self):
        """初始化技能触发器"""
        self.logger = get_logger("SkillTrigger")
        self.detector = ContextDetector()

    def detect_context(self) -> Dict[str, Any]:
        """
        检测当前上下文

        Returns:
            Dict[str, Any]: 上下文信息
        """
        return self.detector.detect_context()

    def recommend_skills(self, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        基于上下文推荐技能

        Args:
            context: 上下文信息（可选，未提供时自动检测）

        Returns:
            List[Dict[str, Any]]: 推荐的技能列表
        """
        if context is None:
            context = self.detect_context()

        recommendations = []

        # 检测到测试文件修改
        if any(f.endswith("_test.go") for f in context.get("file_changes", {}).get("files", [])):
            recommendations.append({
                "skill": "/go-sdk-ut",
                "reason": "检测到测试文件修改",
                "confidence": 0.8
            })

        # 检测到 API 变更
        if self.detector.detect_api_changes(context):
            recommendations.append({
                "skill": "/sdk-doc",
                "reason": "检测到 API 接口变更",
                "confidence": 0.9
            })

        # 检测到性能相关代码
        if self.detector.detect_performance_code(context):
            recommendations.append({
                "skill": "/go-sdk-perf",
                "reason": "检测到性能敏感代码",
                "confidence": 0.7
            })

        # 检测到安全相关代码
        if self.detector.detect_security_code(context):
            recommendations.append({
                "skill": "/go-sdk-fuzz",
                "reason": "检测到安全敏感代码（认证、签名）",
                "confidence": 0.85
            })

        # 按置信度排序
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        self.logger.info(f"推荐技能: {recommendations}")
        return recommendations

    def get_skill_status(self, task_path: str) -> str:
        """
        获取技能状态

        Args:
            task_path: 任务路径

        Returns:
            str: 状态（pending/in_progress/completed）
        """
        from pathlib import Path

        status_file = Path(task_path) / "STATUS"
        if not status_file.exists():
            return "pending"

        with open(status_file, 'r') as f:
            return f.read().strip()

    def should_trigger_skill(
        self,
        skill_name: str,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        判断是否应该触发技能

        Args:
            skill_name: 技能名称
            condition: 触发条件
            context: 上下文信息

        Returns:
            bool: 是否应该触发
        """
        # 解析触发条件
        # 示例条件：
        # - "when _test.go files are updated"
        # - "when STATUS file = 'completed'"
        # - "when all subtasks completed"

        if "_test.go" in condition:
            test_files = context.get("test_files", [])
            return len(test_files) > 0

        if "STATUS" in condition:
            # 检查状态文件
            from pathlib import Path
            status_file = Path(self.detector.working_dir) / "STATUS"
            if not status_file.exists():
                return False

            with open(status_file, 'r') as f:
                status = f.read().strip()
                return condition.split("=")[1].strip().strip("'\"") == status

        if "all subtasks" in condition and "completed" in condition:
            # 检查所有子任务是否完成
            subtasks_dir = Path(self.detector.working_dir) / "subtasks"
            if not subtasks_dir.exists():
                return False

            for task_dir in subtasks_dir.glob("task-*"):
                status = self.get_skill_status(str(task_dir))
                if status != "completed":
                    return False

            return True

        return False
