"""
上下文检测模块

用于检测当前开发上下文，推荐相关技能。
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from .logger import get_logger


class ContextDetector:
    """上下文检测器"""

    def __init__(self):
        """初始化上下文检测器"""
        self.logger = get_logger("ContextDetector")
        self.working_dir = Path.cwd()

    def detect_context(self) -> Dict[str, Any]:
        """
        检测当前上下文

        Returns:
            Dict[str, Any]: 上下文信息
        """
        context = {
            "file_changes": self._detect_file_changes(),
            "git_status": self._get_git_status(),
            "test_files": self._list_test_files(),
            "doc_files": self._list_doc_files(),
            "go_files": self._list_go_files(),
        }

        self.logger.debug(f"检测到上下文: {context}")
        return context

    def _detect_file_changes(self) -> Dict[str, Any]:
        """检测文件变化"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

            return {
                "changed_count": len(changed_files),
                "files": changed_files,
                "has_changes": len(changed_files) > 0
            }
        except Exception as e:
            self.logger.warning(f"检测文件变化失败: {e}")
            return {"changed_count": 0, "files": [], "has_changes": False}

    def _get_git_status(self) -> Dict[str, Any]:
        """获取 Git 状态"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

            modified = []
            added = []
            deleted = []

            for line in status_lines:
                status = line[:2]
                file = line[3:]
                if 'M' in status:
                    modified.append(file)
                elif 'A' in status:
                    added.append(file)
                elif 'D' in status:
                    deleted.append(file)

            return {
                "modified": modified,
                "added": added,
                "deleted": deleted,
                "has_changes": bool(modified or added or deleted)
            }
        except Exception as e:
            self.logger.warning(f"获取 Git 状态失败: {e}")
            return {
                "modified": [],
                "added": [],
                "deleted": [],
                "has_changes": False
            }

    def _list_test_files(self) -> List[str]:
        """列出测试文件"""
        test_files = list(self.working_dir.glob("**/*_test.go"))
        return [str(f.relative_to(self.working_dir)) for f in test_files]

    def _list_doc_files(self) -> List[str]:
        """列出文档文件"""
        doc_files = []
        docs_dir = self.working_dir / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("**/*.md"))

        return [str(f.relative_to(self.working_dir)) for f in doc_files]

    def _list_go_files(self) -> List[str]:
        """列出 Go 源文件"""
        go_files = list(self.working_dir.glob("**/*.go"))
        # 排除测试文件和生成的文件
        go_files = [
            f for f in go_files
            if "_test.go" not in f.name
            and "gen/" not in str(f)
        ]

        return [str(f.relative_to(self.working_dir)) for f in go_files]

    def detect_api_changes(self, context: Dict[str, Any]) -> bool:
        """
        检测 API 变更

        Args:
            context: 上下文信息

        Returns:
            bool: 是否有 API 变更
        """
        go_files = context.get("go_files", [])

        # 检查是否修改了 client 文件
        has_client_changes = any(
            "client" in f or "trait_" in f
            for f in go_files
        )

        return has_client_changes

    def detect_performance_code(self, context: Dict[str, Any]) -> bool:
        """
        检测性能相关代码

        Args:
            context: 上下文信息

        Returns:
            bool: 是否有性能代码
        """
        go_files = context.get("go_files", [])

        # 检查是否涉及性能相关
        has_perf_keywords = any(
            any(keyword in f.lower() for keyword in ["buffer", "pool", "cache", "optimize"])
            for f in go_files
        )

        return has_perf_keywords

    def detect_security_code(self, context: Dict[str, Any]) -> bool:
        """
        检测安全相关代码

        Args:
            context: 上下文信息

        Returns:
            bool: 是否有安全代码
        """
        go_files = context.get("go_files", [])

        # 检查是否涉及认证、签名等
        has_security_keywords = any(
            any(keyword in f.lower() for keyword in ["auth", "sign", "encrypt", "token"])
            for f in go_files
        )

        return has_security_keywords
