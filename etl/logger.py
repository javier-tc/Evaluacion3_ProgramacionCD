import sys
from pathlib import Path

from loguru import logger

from etl.config import get_settings


def setup_logger() -> None:
    settings = get_settings()
    logs_dir: Path = settings.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )
    logger.add(
        logs_dir / "etl_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="30 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )


setup_logger()
