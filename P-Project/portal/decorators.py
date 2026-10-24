# Teen decorators: timer, log_call, require_role. Teeno ek dusre ke upar stack ho sakte hain.
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
            log.info("%s took %.4f sec", func.__name__, time.perf_counter() - start)
    return wrapper


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log.info("CALL %s args=%s kwargs=%s", func.__name__, args[1:], kwargs)   # args[0] self hai
        result = func(*args, **kwargs)
        log.info("DONE %s", func.__name__)
        return result
    return wrapper


def require_role(role):
    # ye decorator argument leta hai, isliye teen levels ke functions hain
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if ROLE_LEVEL.get(self.role, 0) < ROLE_LEVEL[role]:
                log.warning("DENIED %s (role=%s, chahiye=%s)", func.__name__, self.role, role)
                raise AccessDeniedError(f"{func.__name__} ke liye '{role}' role chahiye, aap '{self.role}' hain")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
