import logging
import os


def setup_logging(log_file, level="INFO"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("portal")
    if logger.handlers:                      # dobara handlers na lagein
        return logger
    logger.setLevel(getattr(logging, level, logging.INFO))

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

    to_file = logging.FileHandler(log_file, encoding="utf-8")     # file mein sab kuch
    to_file.setFormatter(fmt)

    to_screen = logging.StreamHandler()                           # screen par sirf ERROR
    to_screen.setLevel(logging.ERROR)
    to_screen.setFormatter(fmt)

    logger.addHandler(to_file)
    logger.addHandler(to_screen)
    return logger
