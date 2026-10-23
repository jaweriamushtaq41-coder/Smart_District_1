"""Stackable decorators: timer, log_call, require_role (Day 7)."""
import functools
import logging
import time

from .exceptions import AccessDeniedError

log = logging.getLogger("portal.decorators")
ROLE_LEVEL = {"viewer": 1, "admin": 2}


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            log.info("%s took %.4fs", func.__name__, time.perf_counter() - start)
    return wrapper


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        shown = args[1:] if args else args      # skip self
        log.info("CALL %s args=%s kwargs=%s", func.__name__, shown, kwargs)
        result = func(*args, **kwargs)
        log.info("DONE %s", func.__name__)
        return result
    return wrapper


def require_role(role):
    """Decorator factory (decorator that accepts arguments)."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if ROLE_LEVEL.get(self.role, 0) < ROLE_LEVEL[role]:
                log.warning("DENIED %s for role=%s (needs %s)", func.__name__, self.role, role)
                raise AccessDeniedError(f"'{func.__name__}' needs role '{role}', you are '{self.role}'")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
