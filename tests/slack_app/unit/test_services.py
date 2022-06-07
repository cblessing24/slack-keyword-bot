from __future__ import annotations

from typing import Optional

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, ChannelName
from slack_app.service_layer.services import list_subscribers, list_subscriptions, subscribe, unsubscribe
from slack_app.service_layer.unit_of_work import AbstractUnitOfWork

from .conftest import FakeRepository


class FakeUnitOfWork(AbstractUnitOfWork[FakeRepository]):
    def __init__(self) -> None:
        self.committed = False
        self.channels = FakeRepository()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_subscription_gets_added() -> None:
    uow = FakeUnitOfWork()
    subscribe(uow, channel_name="general", subscriber="bob", keyword="hello")
    subscriptions = list_subscriptions(uow, channel_name="general", subscriber="bob")
    assert subscriptions == {"hello"}


def test_added_subscription_gets_committed() -> None:
    uow = FakeUnitOfWork()
    subscribe(uow, channel_name="general", subscriber="bob", keyword="hello")
    assert issubclass(FakeUnitOfWork, AbstractUnitOfWork)
    assert uow.committed


def test_list_keywords_errors_for_unknown_channe() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown channel"):
        list_subscriptions(uow, channel_name="general", subscriber="bob")


def test_subscribers_are_returned() -> None:
    uow = FakeUnitOfWork()
    in_keyword = ("general", "bob", "World")
    out_keyword = ("general", "alice", "World")
    author_keyword = ("general", "john", "Goodbye")
    for subscription in [in_keyword, out_keyword, author_keyword]:
        subscribe(uow, *subscription)
    subscribers = list_subscribers(uow, channel_name="general", author="john", text="Goodbye World")
    assert subscribers == {"bob", "alice"}


def test_get_subscribers_errors_for_unknown_channel() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown channel"):
        list_subscribers(uow, channel_name="general", author="john", text="Goodbye World")


def test_can_unsubscribe() -> None:
    uow = FakeUnitOfWork()
    subscribe(uow, channel_name="general", subscriber="bob", keyword="hello")
    unsubscribe(uow, channel_name="general", subscriber="bob", keyword="hello")
    subscriptions = list_subscriptions(uow, channel_name="general", subscriber="bob")
    assert subscriptions == set()


def test_unsubscribe_errors_for_unknown_channel() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown channel"):
        unsubscribe(uow, channel_name="general", subscriber="bob", keyword="hello")


def test_unsubscribe_errors_for_unknown_subscription() -> None:
    uow = FakeUnitOfWork()
    subscribe(uow, channel_name="general", subscriber="john", keyword="hello")
    with pytest.raises(ValueError, match="Unknown subscription"):
        unsubscribe(uow, channel_name="general", subscriber="bob", keyword="hello")
