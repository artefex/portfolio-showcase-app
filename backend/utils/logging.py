import logging
import sys


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("recipe_chatbot")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    return logger
