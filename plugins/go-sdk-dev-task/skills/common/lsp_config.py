"""
LSP 配置支持模块

为 Go 项目生成和管理 gopls 配置文件，确保代码生成符合 LSP 最佳实践。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


class LSPConfigGenerator:
    """LSP 配置生成器"""

    def __init__(self, project_root: str):
        """初始化 LSP 配置生成器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)

    def generate_gopls_settings(self) -> Dict[str, Any]:
        """生成 gopls 设置配置

        Returns:
            Dict[str, Any]: gopls 设置字典
        """
        return {
            "ui.diagnostic.staticcheck": True,
            "ui.diagnostic.analyses": {
                # 基础分析
                "unreachable": True,
                "unusedvariable": True,
                "unusedimport": True,
                "unusedparam": True,
                "shadowing": True,
                "assign": True,
                "fieldalignment": True,
                "ineffassign": True,
                "nilness": True,
                "noewvars": True,
                "noresultvalues": True,
                "structpack": True,
                "unnecessarystring": True,
                "unreachable": True,
                "unused": True,

                # Google Go 特定分析
                "S1019": True,  # use of fmt.Sprint instead of fmt.Sprintf
                "S1020": True,  # don't use fmt.Sprintf for strings without format specifiers
                "S1021": True,  # don't use fmt.Sprintf for string concatenation
            },
            "build.experimentalWorkspaceModule": True,
            "build.experimentalPackageCache": True,
            "ui.completion.usePlaceholders": True,
            "ui.completion.postfix": True,
            "ui.completion.matcher": "fuzzy",
            "ui.completion.filters": {
                "unimported": False,
                "unnamed": True,
                "valueKeywords": False
            },
            "ui.semanticTokens": True,
            "ui.navigation.importShortcut": "both",
            "formatting.gofumpt": True,
            "formatting.local": "goimports",
        }

    def generate_gopls_workspace_config(self) -> Dict[str, Any]:
        """生成 gopls 工作空间配置

        Returns:
            Dict[str, Any]: gopls 工作空间配置字典
        """
        return {
            "usePlaceholders": True,
            "completeUnimported": True,
            "deepCompletion": True,
            "matcher": "fuzzy",
            "staticcheck": True,
            "experimentalPostfixCompletions": True,
            "experimentalWorkspaceModule": True,
            "analyses": {
                "unreachable": True,
                "unusedvariable": True,
                "unusedimport": True,
                "shadowing": True,
                "unusedparams": True,
            }
        }

    def generate_vscode_settings(self) -> Dict[str, Any]:
        """生成 VSCode 设置配置

        Returns:
            Dict[str, Any]: VSCode 设置字典
        """
        return {
            "go.useLanguageServer": True,
            "go.lintTool": "golangci-lint",
            "go.lintOnSave": "workspace",
            "go.vetOnSave": "workspace",
            "go.buildOnSave": "workspace",
            "go.testFlags": [
                "-v",
                "-race",
                "-coverprofile=coverage.out",
                "-covermode=atomic"
            ],
            "go.testTimeout": "30s",
            "go.coverageDecorator": {
                "type": "gutter",
                "highlight": "light",
                "showRelativeCoverage": True
            },
            "[go]": {
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": "explicit"
                },
                "editor.suggest.snippetsPreventQuickSuggestions": False,
                "editor.tabCompletion": true,
            },
            "gopls": self.generate_gopls_settings(),
            "files.exclude": {
                "**/vendor": True,
                "**/.git": True,
                "**/.DS_Store": True,
                "**/node_modules": True
            }
        }

    def generate_go_env_config(self) -> Dict[str, str]:
        """生成 Go 环境配置

        Returns:
            Dict[str, str]: Go 环境变量字典
        """
        return {
            "GOPATH": str(self.project_root),
            "GOMODCACHE": os.path.join(self.project_root, ".cache", "go-mod"),
            "GOCACHE": os.path.join(self.project_root, ".cache", "go-build"),
            "GOPROXY": "https://goproxy.cn,direct",  # 中国镜像
            "GOSUMDB": "https://goproxy.cn/sumdb/sumdb/1",
            "GO111MODULE": "on",
            "CGO_ENABLED": "0",  # 禁用 CGO 以提高构建速度
            "GOFLAGS": "-mod=mod",
        }

    def generate_golangci_lint_config(self) -> Dict[str, Any]:
        """生成 golangci-lint 配置

        Returns:
            Dict[str, Any]: golangci-lint 配置字典
        """
        return {
            "run": {
                # Google Go 推荐的 linters
                "govet": {
                    "enable-all": True,
                    "disable": ["shadow"]  # 使用专门的 shadow linter
                },
                "golint": {
                    "min-confidence": 0.8
                },
                "staticcheck": True,
                "unused": True,
                "varcheck": True,
                "structcheck": True,
                "errcheck": True,
                "gosimple": True,
            },
            "linters": {
                "enable": [
                    # 基础 linters
                    "govet",
                    "golint",
                    "staticcheck",
                    "unused",
                    "varcheck",
                    "structcheck",
                    "errcheck",
                    "gosimple",
                    "ineffassign",
                    "deadcode",
                    "typecheck",

                    # 性能和安全 linters
                    "gocyclo",
                    "gosec",
                    "gas",
                    "misspell",
                    "gofmt",
                    "goimports",

                    # 现代 linters
                    "revive",
                    "exhaustivestruct",
                    "goconst",
                    "gocognit",
                ]
            },
            "linters-settings": {
                "govet": {
                    "check-shadowing": True,
                    "enable-all": True,
                },
                "revive": {
                    "confidence": 0.8,
                    "rules": [
                        {"name": "exported"},
                        {"name": "blank-imports"},
                        {"name": "context-as-argument"},
                        {"name": "context-keys-type"},
                        {"name": "dot-imports"},
                        {"name": "error-return"},
                        {"name": "error-strings"},
                        {"name": "error-naming"},
                        {"name": "if-return"},
                        {"name": "increment-decrement"},
                        {"name": "var-naming"},
                        {"name": "var-declaration"},
                        {"name": "package-comments"},
                        {"name": "range"},
                        {"name": "receiver-naming"},
                        {"name": "time-naming"},
                        {"name": "unexported-return"},
                        {"name": "indent-error-flow"},
                        {"name": "errorf"},
                        {"name": "empty-block"},
                        {"name": "superfluous-else"},
                        {"name": "unused-parameter"},
                        {"name": "confusing-naming"},
                        {"name": "get-return"},
                        {"name": "modifies-parameter"},
                        {"name": "confusing-results"},
                    ]
                },
                "gosec": {
                    "includes": ["G101", "G102", "G103", "G104", "G106", "G107"],
                }
            },
            "issues": {
                "exclude": [],
                "exclude-rules": [],
                "max-issues-per-linter": 0,
                "max-same-issues": 3,
            },
            "output": {
                "format": "colored-line-number",
                "print-issued-lines": True,
                "print-linter-name": True,
                "uniq-by-line": True,
                "sort-results": True,
            }
        }

    def generate_pre_commit_config(self) -> Dict[str, Any]:
        """生成 pre-commit 钩子配置

        Returns:
            Dict[str, Any]: pre-commit 配置字典
        """
        return {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.4.0",
                    "hooks": [
                        {
                            "id": "trailing-whitespace",
                            "args": ["--markdown-line-breaker=MD033"]
                        },
                        {
                            "id": "end-of-file-fixer"
                        },
                        {
                            "id": "check-yaml"
                        },
                        {
                            "id": "check-added-large-files"
                        }
                    ]
                },
                {
                    "repo": "https://github.com/golangci/golangci-lint",
                    "rev": "latest",
                    "hooks": [
                        {
                            "id": "golangci-lint",
                            "entry": "golangci-lint run",
                            "types": ["go"],
                            "language": "golang"
                        }
                    ]
                },
                {
                    "repo": "https://github.com/dnephin/pre-commit-golang",
                    "rev": "v0.5.1",
                    "hooks": [
                        {
                            "id": "go-fmt",
                            "files": r"\.go$"
                        },
                        {
                            "id": "go-lint",
                            "files": r"\.go$"
                        },
                        {
                            "id": "go-mod-tidy",
                            "files": r"\.mod$"
                        }
                    ]
                }
            ]
        }

    def write_gopls_config(self) -> Path:
        """写入 gopls 配置文件

        Returns:
            Path: 配置文件路径
        """
        config_dir = self.project_root / ".vscode"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "settings.json"
        settings = self.generate_vscode_settings()

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

        return config_file

    def write_golangci_config(self) -> Path:
        """写入 golangci-lint 配置文件

        Returns:
            Path: 配置文件路径
        """
        config_file = self.project_root / ".golangci.yml"
        settings = self.generate_golangci_lint_config()

        with open(config_file, 'w', encoding='utf-8') as f:
            # 写入 YAML 格式（简化版）
            f.write("# golangci-lint 配置文件\n")
            f.write("# 符合 Google Go 规范的 lint 配置\n\n")
            f.write("linters:\n")
            for linter in settings['linters']['enable']:
                f.write(f"  - {linter}\n")

            f.write("\nlinters-settings:\n")
            f.write("  govet:\n")
            f.write("    check-shadowing: true\n")
            f.write("    enable-all: true\n")

        return config_file

    def write_pre_commit_config(self) -> Path:
        """写入 pre-commit 配置文件

        Returns:
            Path: 配置文件路径
        """
        config_file = self.project_root / ".pre-commit-config.yaml"
        settings = self.generate_pre_commit_config()

        with open(config_file, 'w', encoding='utf-8') as f:
            # 写入 YAML 格式
            f.write("repos:\n")
            for repo in settings['repos']:
                f.write(f"  - repo: {repo['repo']}\n")
                f.write(f"    rev: {repo['rev']}\n")
                f.write("    hooks:\n")
                for hook in repo['hooks']:
                    f.write(f"      - id: {hook['id']}\n")
                    if 'files' in hook:
                        f.write(f"        files: '{hook['files']}'\n")
                    if 'language' in hook:
                        f.write(f"        language: {hook['language']}\n")

        return config_file

    def write_env_file(self) -> Path:
        """写入 Go 环境变量文件

        Returns:
            Path: 环境变量文件路径
        """
        env_file = self.project_root / ".env.go"
        env_vars = self.generate_go_env_config()

        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# Go 环境变量配置\n")
            f.write("# 符合 Google Go 规范的环境设置\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        return env_file

    def generate_all_configs(self) -> Dict[str, Path]:
        """生成所有 LSP 相关配置文件

        Returns:
            Dict[str, Path]: 配置文件路径字典
        """
        return {
            'gopls_settings': self.write_gopls_config(),
            'golangci_config': self.write_golangci_config(),
            'pre_commit_config': self.write_pre_commit_config(),
            'env_file': self.write_env_file()
        }


class GoProjectValidator:
    """Go 项目验证器"""

    def __init__(self, project_root: str):
        """初始化 Go 项目验证器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)

    def validate_project_structure(self) -> Dict[str, List[str]]:
        """验证项目结构符合 Google Go 规范

        Returns:
            Dict[str, List[str]]: 验证结果
        """
        errors = []
        warnings = []

        # 检查 go.mod 文件
        go_mod = self.project_root / "go.mod"
        if not go_mod.exists():
            errors.append("缺少 go.mod 文件")
        else:
            warnings.append("go.mod 文件存在")

        # 检查 vendor 目录
        vendor_dir = self.project_root / "vendor"
        if vendor_dir.exists():
            warnings.append("vendor 目录存在，建议使用 Go modules")

        # 检查文档
        readme = self.project_root / "README.md"
        if not readme.exists():
            warnings.append("缺少 README.md 文件")

        # 检查 .gitignore
        gitignore = self.project_root / ".gitignore"
        if not gitignore.exists():
            warnings.append("缺少 .gitignore 文件")

        return {
            'errors': errors,
            'warnings': warnings,
            'valid': len(errors) == 0
        }

    def validate_package_structure(self) -> Dict[str, Any]:
        """验证包结构符合 Google Go 规范

        Returns:
            Dict[str, Any]: 验证结果
        """
        # 查找所有包
        packages = []
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != 'vendor':
                # 检查是否为 Go 包
                go_files = list(item.glob("*.go"))
                if go_files:
                    packages.append(item.name)

        return {
            'packages': packages,
            'count': len(packages),
            'recommendations': [
                "每个包应该有明确的职责",
                "包名应该简洁、描述性强",
                "避免循环依赖"
            ]
        }


def validate_lsp_compatibility(project_root: str) -> Dict[str, Any]:
    """验证项目的 LSP 兼容性

    Args:
        project_root: 项目根目录

    Returns:
        Dict[str, Any]: 验证结果
    """
    validator = GoProjectValidator(project_root)

    structure_validation = validator.validate_project_structure()
    package_validation = validator.validate_package_structure()

    return {
        'structure': structure_validation,
        'packages': package_validation,
        'compatible': structure_validation['valid'],
        'recommendations': structure_validation['warnings'] + package_validation['recommendations']
    }


# 使用示例
if __name__ == "__main__":
    # 生成配置示例
    generator = LSPConfigGenerator("/path/to/project")

    # 生成所有配置
    config_files = generator.generate_all_configs()
    print("生成的配置文件:")
    for name, path in config_files.items():
        print(f"  {name}: {path}")

    # 验证项目
    validation = validate_lsp_compatibility("/path/to/project")
    print(f"项目验证结果: {validation}")