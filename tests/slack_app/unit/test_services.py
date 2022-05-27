from __future__ import annotations

from typing import Iterable, Optional

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, Keyword, User, Word
from slack_app.service_layer.services import add_keyword, deactivate_keyword, get_subscribers, list_keywords
from slack_app.service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
    def __init__(self, keywords: Optional[set[Keyword]] = None) -> None:
        self.keywords = keywords if keywords is not None else set()

    def add(self, keyword: Keyword) -> None:
        self.keywords.add(keyword)

    def get(self, channel: Channel) -> list[Keyword]:
        return [k for k in self.keywords if k.channel == channel]

    @staticmethod
    def for_keywords(keywords: Iterable[tuple[str, str, str]]) -> FakeRepository:
        return FakeRepository(
            {
                Keyword(
                    channel=Channel(channel),
                    subscriber=User(subscriber),
                    word=Word(word),
                )
                for channel, subscriber, word in keywords
            }
        )


class FakeUnitOfWork(AbstractUnitOfWork[FakeRepository]):
    def __init__(self) -> None:
        self.committed = False
        self.keywords = FakeRepository()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_keyword_gets_added() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel="general", user="bob", word="hello")
    keywords = list_keywords(uow, channel="general", subscriber="bob")
    assert keywords == {"hello"}


def test_added_keyword_gets_committed() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel="general", user="bob", word="hello")
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
    subscribers = get_subscribers(uow, channel="general", author="john", text="Goodbye World")
    assert subscribers == {"bob", "alice"}


def test_keyword_can_be_deactivated() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel="general", user="bob", word="hello")
    deactivate_keyword(uow, channel="general", subscriber="bob", word="hello")
    keywords = list_keywords(uow, channel="general", subscriber="bob")
    assert keywords == set()


def test_error_gets_raised_if_unknown_keyword_is_deactivated() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown keyword"):
        deactivate_keyword(uow, channel="general", subscriber="bob", word="hello")
