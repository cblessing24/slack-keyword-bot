from typing import Any, Protocol

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from slack_app.adapters.orm import metadata, start_mappers
from slack_app.domain.model import Channel, Keyword, User, Word


class KeywordCreator(Protocol):
    def __call__(self, channel: str = ..., subscriber: str = ..., word: str = ...) -> Keyword:
        ...


@pytest.fixture
def create_keyword() -> KeywordCreator:
    def create(channel: str = "mychannel", subscriber: str = "bob", word: str = "hello") -> Keyword:
        return Keyword(channel=Channel(channel), subscriber=User(subscriber), word=Word(word))

    return create


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
