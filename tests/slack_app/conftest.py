from typing import Any, Protocol

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from slack_app.adapters.orm import metadata, start_mappers
from slack_app.domain.model import ChannelName, Keyword, User, Word


class KeywordCreator(Protocol):
    def __call__(
        self, channel_name: str = ..., subscriber: str = ..., word: str = ..., unsubscribed: bool = ...
    ) -> Keyword:
        ...


@pytest.fixture
def create_keyword() -> KeywordCreator:
    def create(
        channel_name: str = "mychannel", subscriber: str = "bob", word: str = "hello", unsubscribed: bool = False
    ) -> Keyword:
        return Keyword(
            channel_name=ChannelName(channel_name),
            subscriber=User(subscriber),
            word=Word(word),
            unsubscribed=unsubscribed,
        )

    return create


@pytest.fixture
def in_memory_db() -> Any:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db: Any) -> Any:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(session_factory: Any) -> Any:
    return session_factory()
