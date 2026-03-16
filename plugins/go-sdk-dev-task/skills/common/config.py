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

    # Subagent 相关配置方法

    def is_subagent_enabled(self) -> bool:
        """
        检查是否启用 subagent 功能

        Returns:
            bool: 如果启用则返回 True，否则返回 False
        """
        return self.get_bool('subagent.enabled', False)

    def get_parallel_workers(self) -> int:
        """
        获取并行工作数

        Returns:
            int: 并行工作数，默认为 2
        """
        return self.get_int('subagent.parallel_workers', 2)

    def get_research_timeout(self) -> float:
        """
        获取研究任务超时时间

        Returns:
            float: 超时时间（秒），默认为 300 秒
        """
        return self.get_float('subagent.research_timeout', 300.0)

    def get_execution_timeout(self) -> float:
        """
        获取执行任务超时时间

        Returns:
            float: 超时时间（秒），默认为 600 秒
        """
        return self.get_float('subagent.execution_timeout', 600.0)

    def get_heartbeat_interval(self) -> float:
        """
        获取心跳间隔

        Returns:
            float: 心跳间隔（秒），默认为 30 秒
        """
        return self.get_float('subagent.heartbeat_interval', 30.0)

    def get_max_retries(self) -> int:
        """
        获取最大重试次数

        Returns:
            int: 最大重试次数，默认为 3
        """
        return self.get_int('subagent.max_retries', 3)

    def get_retry_delay(self) -> float:
        """
        获取重试延迟

        Returns:
            float: 重试延迟（秒），默认为 2.0 秒
        """
        return self.get_float('subagent.retry_delay', 2.0)

    def get_message_queue_size(self) -> int:
        """
        获取消息队列大小

        Returns:
            int: 消息队列大小，默认为 100
        """
        return self.get_int('subagent.message_queue_size', 100)

    def get_subagent_config(self, skill_id: str) -> Dict[str, Any]:
        """
        获取特定技能的 subagent 配置

        Args:
            skill_id: 技能标识

        Returns:
            Dict[str, Any]: subagent 配置字典
        """
        subagent_configs = self.get_dict('subagent.skills', {})
        return subagent_configs.get(skill_id, {})

    def is_skill_subagent_enabled(self, skill_id: str) -> bool:
        """
        检查特定技能是否启用 subagent

        Args:
            skill_id: 技能标识

        Returns:
            bool: 如果启用则返回 True，否则返回 False
        """
        skill_config = self.get_subagent_config(skill_id)
        if skill_config:
            return skill_config.get('enabled', False)
        return self.is_subagent_enabled()

    def get_skill_parallel_workers(self, skill_id: str) -> int:
        """
        获取特定技能的并行工作数

        Args:
            skill_id: 技能标识

        Returns:
            int: 并行工作数
        """
        skill_config = self.get_subagent_config(skill_id)
        if skill_config and 'parallel_workers' in skill_config:
            return skill_config['parallel_workers']
        return self.get_parallel_workers()

    def get_skill_timeout(self, skill_id: str, default: Optional[float] = None) -> float:
        """
        获取特定技能的超时时间

        Args:
            skill_id: 技能标识
            default: 默认超时时间（秒）

        Returns:
            float: 超时时间（秒）
        """
        skill_config = self.get_subagent_config(skill_id)
        if skill_config and 'timeout' in skill_config:
            return skill_config['timeout']
        return default or self.get_execution_timeout()

    def get_default_subagent_config(self) -> Dict[str, Any]:
        """
        获取默认的 subagent 配置

        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            'enabled': False,
            'parallel_workers': 2,
            'research_timeout': 300.0,
            'execution_timeout': 600.0,
            'heartbeat_interval': 30.0,
            'max_retries': 3,
            'retry_delay': 2.0,
            'message_queue_size': 100,
            'skills': {}
        }
