"""
重试机制模块

提供指数退避等重试策略。
"""

import time
import functools
from typing import Optional, Type, Callable, Any, Tuple
from .logger import get_logger


class RetryConfig:
    """重试配置"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
        jitter: bool = False
    ):
        """
        初始化重试配置

        Args:
            max_attempts: 最大重试次数
            base_delay: 基础延迟（秒）
            max_delay: 最大延迟（秒）
            exponential: 是否使用指数退避
            jitter: 是否添加随机抖动
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.jitter = jitter


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    jitter: bool = False,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential: 是否使用指数退避
        jitter: 是否添加随机抖动
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数

    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(func.__name__)
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(f"重试 {max_attempts} 次后仍然失败")
                        raise

                    # 计算延迟
                    delay = base_delay
                    if exponential:
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

                    # 添加抖动
                    if jitter:
                        import random
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"第 {attempt} 次尝试失败: {e}，"
                        f"{delay:.1f} 秒后重试..."
                    )

                    # 调用回调
                    if on_retry:
                        on_retry(attempt, e)

                    time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


class RetryManager:
    """重试管理器"""

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        初始化重试管理器

        Args:
            config: 重试配置
        """
        self.config = config or RetryConfig()
        self.logger = get_logger(self.__class__.__name__)

    def execute(
        self,
        func: Callable,
        *args: Any,
        exceptions: Optional[Tuple[Type[Exception], ...]] = None,
        **kwargs: Any
    ) -> Any:
        """
        执行函数，支持重试

        Args:
            func: 要执行的函数
            *args: 位置参数
            exceptions: 需要重试的异常类型
            **kwargs: 关键字参数

        Returns:
            Any: 函数返回值

        Raises:
            Exception: 重试失败后的最后一个异常
        """
        if exceptions is None:
            exceptions = (Exception,)

        last_exception = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e

                if attempt == self.config.max_attempts:
                    self.logger.error(f"重试 {self.config.max_attempts} 次后仍然失败")
                    raise

                # 计算延迟
                delay = self.config.base_delay
                if self.config.exponential:
                    delay = min(
                        self.config.base_delay * (2 ** (attempt - 1)),
                        self.config.max_delay
                    )

                # 添加抖动
                if self.config.jitter:
                    import random
                    delay = delay * (0.5 + random.random())

                self.logger.warning(
                    f"第 {attempt} 次尝试失败: {e}，"
                    f"{delay:.1f} 秒后重试..."
                )

                time.sleep(delay)

        raise last_exception

    def retry_decorator(
        self,
        exceptions: Optional[Tuple[Type[Exception], ...]] = None
    ) -> Callable:
        """
        创建重试装饰器

        Args:
            exceptions: 需要重试的异常类型

        Returns:
            Callable: 装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self.execute(func, *args, exceptions=exceptions, **kwargs)
            return wrapper
        return decorator
