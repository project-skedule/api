# pyright: reportUnusedImport=false, reportOptionalMemberAccess=false

import json
import logging
from pathlib import Path
from typing import Any, Dict
from loguru import logger


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record: Any):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame = logging.currentframe()
        if frame is not None:
            depth = 2

            while (
                frame.f_code.co_filename == logging.__file__
            ):  # type: reportOptionalMemberAccess=false
                frame = frame.f_back
                depth += 1

            log = logger.bind(request_id="app")
            log.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )


class CustomizeLogger:
    @classmethod
    def make_logger(cls, config_path: Path):

        config = cls.load_logging_config(config_path)
        logging_config = config.get("logger")

        return cls.customize_logging(
            logging_config.get("path"),
            level=logging_config.get("level", "INFO"),
            rotation=logging_config.get("rotation"),
            format=logging_config.get("format"),
            mode=logging_config.get("mode", "a"),
            backtrace=logging_config.get("backtrace", False),
            enqueue=logging_config.get("enqueue", False),
        )

    @classmethod
    def customize_logging(cls, filepath: Path, **kwargs: Dict[str, Any]):
        logger.remove()
        logger.add(str(filepath), **kwargs)
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        # logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        # for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
        # _logger = logging.getLogger(_log)
        # _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)

    @classmethod
    def load_logging_config(cls, config_path: Path):
        config = None
        with open(config_path) as config_file:
            config = json.load(config_file)
        return config
