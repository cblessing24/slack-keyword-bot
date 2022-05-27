from __future__ import annotations

from typing import Iterable, Optional

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, ChannelName
from slack_app.service_layer.services import add_keyword, deactivate_keyword, get_subscribers, list_keywords
from slack_app.service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
    def __init__(self, channels: Optional[set[Channel]] = None) -> None:
        self.channels = channels if channels is not None else set()

    def add(self, channel: Channel) -> None:
        self.channels.add(channel)

    def get(self, channel_name: ChannelName) -> Channel | None:
        try:
            return next(c for c in self.channels if c.channel_name == channel_name)
        except StopIteration:
            return None


class FakeUnitOfWork(AbstractUnitOfWork[FakeRepository]):
    def __init__(self) -> None:
        self.committed = False
        self.channels = FakeRepository()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_keyword_gets_added() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel_name="general", user="bob", word="hello")
    keywords = list_keywords(uow, channel_name="general", subscriber="bob")
    assert keywords == {"hello"}


def test_added_keyword_gets_committed() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel_name="general", user="bob", word="hello")
    assert issubclass(FakeUnitOfWork, AbstractUnitOfWork)
    assert uow.committed


def test_subscribers_are_returned() -> None:
    uow = FakeUnitOfWork()
    in_keyword = ("general", "bob", "World")
    out_keyword = ("general", "alice", "World")
    author_keyword = ("general", "john", "Goodbye")
    keywords = [in_keyword, out_keyword, author_keyword]
    for keyword in keywords:
        add_keyword(uow, *keyword)
    subscribers = get_subscribers(uow, channel_name="general", author="john", text="Goodbye World")
    assert subscribers == {"bob", "alice"}


def test_keyword_can_be_deactivated() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel_name="general", user="bob", word="hello")
    deactivate_keyword(uow, channel_name="general", subscriber="bob", word="hello")
    keywords = list_keywords(uow, channel_name="general", subscriber="bob")
    assert keywords == set()


def test_error_gets_raised_if_unknown_keyword_is_deactivated() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel_name="general", user="john", word="hello")
    with pytest.raises(ValueError, match="Unknown keyword"):
        deactivate_keyword(uow, channel_name="general", subscriber="bob", word="hello")
