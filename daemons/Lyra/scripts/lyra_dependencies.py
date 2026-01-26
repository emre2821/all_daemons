from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Optional

DEPENDENCY_INSTALL_MESSAGE = (
    "Missing GitHub dependencies. Install with: "
    "pip install PyGithub gitpython PyYAML python-dotenv tenacity requests"
)


def require_git_dependencies(has_git: bool) -> None:
    if not has_git:
        raise RuntimeError(DEPENDENCY_INSTALL_MESSAGE)


@dataclass(frozen=True)
class TenacityFallback:
    available: bool
    retry: Callable
    stop_after_attempt: Callable
    wait_exponential: Callable
    retry_if_exception_type: Callable


def load_tenacity(logger: Optional[logging.Logger] = None) -> TenacityFallback:
    try:
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        return TenacityFallback(
            available=True,
            retry=retry,
            stop_after_attempt=stop_after_attempt,
            wait_exponential=wait_exponential,
            retry_if_exception_type=retry_if_exception_type,
        )
    except ImportError:
        def retry(*dargs, **dkwargs):
            def decorator(func):
                return func
            return decorator

        class stop_after_attempt:
            def __init__(self, max_attempt_number: int):
                self.max_attempt_number = max_attempt_number

            def __call__(self, *args, **kwargs):
                return False

        def wait_exponential(multiplier: float = 1, max: Optional[int] = 10):
            return lambda *args, **kwargs: None

        def retry_if_exception_type(exception_types):
            return lambda *args, **kwargs: False

        if logger:
            logger.warning("tenacity not installed; rate-limit retries disabled.")
        return TenacityFallback(
            available=False,
            retry=retry,
            stop_after_attempt=stop_after_attempt,
            wait_exponential=wait_exponential,
            retry_if_exception_type=retry_if_exception_type,
        )
