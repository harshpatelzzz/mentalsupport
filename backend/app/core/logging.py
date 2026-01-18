import logging
import sys
from typing import Any


def setup_logging() -> logging.Logger:
    """
    Configure application logging.
    Returns configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("neurosupport")
    return logger


logger = setup_logging()
