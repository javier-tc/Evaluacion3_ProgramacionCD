#!/usr/bin/env python3
"""crea tablas de forma idempotente usando sqlalchemy."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger

from etl.models import Base, get_engine


def migrate() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("migracion completada: tablas creadas o verificadas")


if __name__ == "__main__":
    migrate()
