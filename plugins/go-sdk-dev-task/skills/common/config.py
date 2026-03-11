"""
配置管理模块

支持 YAML 配置文件和环境变量覆盖。
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigError(Exception):
    """配置错误"""
    pass


class Config:
    """配置管理器"""

    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，默认为 None
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}

        # 加载配置
        if config_file and config_file.exists():
            self.load(config_file)

    def load(self, config_file: Path) -> None:
        """
        加载配置文件

        Args:
            config_file: 配置文件路径

        Raises:
            ConfigError: 配置文件加载失败
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix in ['.yaml', '.yml']:
                    if not YAML_AVAILABLE:
                        raise ConfigError(
                            "PyYAML 未安装，请运行: pip install pyyaml"
                        )
                    self._config = yaml.safe_load(f)
                elif config_file.suffix == '.json':
                    self._config = json.load(f)
                else:
                    raise ConfigError(f"不支持的配置文件格式: {config_file.suffix}")

        except yaml.YAMLError as e:
            raise ConfigError(f"YAML 解析错误: {e}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"JSON 解析错误: {e}")
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点表示法（如 'database.host'）
            default: 默认值

        Returns:
            Any: 配置值
        """
        # 首先检查环境变量
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # 从配置文件获取
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键，支持点表示法
            value: 配置值
        """
        keys = key.split('.')
        config = self._config

        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置值"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置值"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置值"""
        value = self.get(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return bool(value)

    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """获取列表配置值"""
        value = self.get(key)
        if value is None:
            return default or []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [v.strip() for v in value.split(',')]
        return [value]

    def get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """获取字典配置值"""
        value = self.get(key)
        if value is None:
            return default or {}
        if isinstance(value, dict):
            return value
        return {}

    def get_path(self, key: str, default: Optional[str] = None) -> Path:
        """获取路径配置值"""
        value = self.get(key, default)
        if value is None:
            return Path.cwd()
        return Path(value).expanduser().resolve()

    def save(self, config_file: Optional[Path] = None) -> None:
        """
        保存配置到文件

        Args:
            config_file: 配置文件路径，默认为初始化时指定的文件
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ConfigError("未指定配置文件路径")

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ConfigError(
                        "PyYAML 未安装，请运行: pip install pyyaml"
                    )
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            elif file_path.suffix == '.json':
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            else:
                raise ConfigError(f"不支持的配置文件格式: {file_path.suffix}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()

    @classmethod
    def from_env(cls, prefix: str = '') -> 'Config':
        """
        从环境变量创建配置

        Args:
            prefix: 环境变量前缀

        Returns:
            Config: 配置对象
        """
        config = cls()
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue

            # 移除前缀，转换为点表示法
            config_key = key[len(prefix):] if prefix else key
            config_key = config_key.lower().replace('_', '.')
            config.set(config_key, value)

        return config

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        从字典创建配置

        Args:
            config_dict: 配置字典

        Returns:
            Config: 配置对象
        """
        config = cls()
        config._config = config_dict.copy()
        return config
