from typing import Any, Protocol

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from slack_app.adapters.orm import metadata, start_mappers
from slack_app.domain.model import ChannelName, Keyword, Subscription, User


class SubscriptionCreator(Protocol):
    def __call__(
        self, channel_name: str = ..., subscriber: str = ..., keyword: str = ..., unsubscribed: bool = ...
    ) -> Subscription:
        ...


@pytest.fixture
def create_subscription() -> SubscriptionCreator:
    def create(
        channel_name: str = "mychannel", subscriber: str = "bob", keyword: str = "hello", unsubscribed: bool = False
    ) -> Subscription:
        return Subscription(
            channel_name=ChannelName(channel_name),
            subscriber=User(subscriber),
            keyword=Keyword(keyword),
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
