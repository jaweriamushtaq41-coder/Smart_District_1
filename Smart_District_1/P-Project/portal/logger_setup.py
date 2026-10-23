"""Logging with file + console handlers at the same time (Day 7)."""
import logging


def setup_logging(log_file, level="INFO") -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("portal")
    if logger.handlers:          # avoid duplicate handlers on re-import
        return logger
    logger.setLevel(getattr(logging, level, logging.INFO))
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)

    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)        # keep terminal UI clean
    console.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger
