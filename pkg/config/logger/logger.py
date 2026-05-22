import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pkg.config.config.config import Config

def setup_logging() -> logging.Logger:
    config = Config()

    log_file       = config.app.log.LOG_FILE
    file_level     = getattr(logging, config.app.log.LOG_FILE_LEVEL, logging.INFO)
    logger_level   = getattr(logging, config.app.log.LOG_LEVEL, logging.DEBUG)
    enable_console = config.app.log.LOG_CONSOLE_ENABLED
    rotation       = config.app.log.ROTATION

    # Prepare directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")

    rotation_dict = vars(rotation)

    root_logger = logging.getLogger()

    # Idempotency
    if getattr(root_logger, "_configured", False):
        return

    root_logger.setLevel(logger_level)

    # ---------- FILE HANDLER ----------
    file_handler = TimedRotatingFileHandler(
        log_file,
        when=rotation_dict.get("when"),
        interval=rotation_dict.get("interval", 1),
        backupCount=rotation_dict.get("backupCount", 7)
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level)

    # Force-flush (critical for multithreaded logging)
    file_handler.flush = lambda *args, **kwargs: file_handler.stream.flush()

    root_logger.addHandler(file_handler)

    # ---------- CONSOLE HANDLER ----------
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logger_level)
        console_handler.flush = lambda *args, **kwargs: console_handler.stream.flush()
        root_logger.addHandler(console_handler)

    # ---------- SQLALCHEMY NOISE CONTROL ----------
    for name in ["sqlalchemy.engine", "sqlalchemy.orm"]:
        sa_logger = logging.getLogger(name)
        sa_logger.setLevel(logging.INFO)
        sa_logger.propagate = False
        sa_logger.addHandler(file_handler)

    root_logger._configured = True
    return root_logger
