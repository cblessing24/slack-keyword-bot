from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from slack_app.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db() -> Any:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db: Any) -> Any:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
