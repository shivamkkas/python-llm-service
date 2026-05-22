from .config.config import Config
from .logger.logger import setup_logging
import logging
from typing import Tuple
def Initialize() -> Tuple[logging.Logger,Config]:
    slog = setup_logging()
    return slog,Config()