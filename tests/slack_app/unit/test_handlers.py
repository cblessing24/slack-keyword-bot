from __future__ import annotations

import pytest

from slack_app.domain import commands
from slack_app.service_layer import messagebus
from slack_app.service_layer.unit_of_work import AbstractUnitOfWork

from .conftest import FakeRepository


class FakeUnitOfWork(AbstractUnitOfWork[FakeRepository]):
    def __init__(self) -> None:
        self.committed = False
        self.channels = FakeRepository()

    def _commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_subscription_gets_added() -> None:
    uow = FakeUnitOfWork()
    messagebus.handle(commands.Subscribe(channel_name="general", subscriber="bob", keyword="hello"), uow=uow)
    subscriptions = messagebus.handle(commands.ListSubscriptions(channel_name="general", subscriber="bob"), uow=uow)
    assert subscriptions == [{"hello"}]


def test_added_subscription_gets_committed() -> None:
    uow = FakeUnitOfWork()
    messagebus.handle(commands.Subscribe(channel_name="general", subscriber="bob", keyword="hello"), uow=uow)
    assert issubclass(FakeUnitOfWork, AbstractUnitOfWork)
    assert uow.committed


def test_list_keywords_errors_for_unknown_channe() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown channel"):
        messagebus.handle(commands.ListSubscriptions(channel_name="general", subscriber="bob"), uow=uow)


def test_subscribers_are_returned() -> None:
    uow = FakeUnitOfWork()
    in_keyword = ("general", "bob", "World")
    out_keyword = ("general", "alice", "World")
    author_keyword = ("general", "john", "Goodbye")
    for subscription in [in_keyword, out_keyword, author_keyword]:
        messagebus.handle(commands.Subscribe(*subscription), uow=uow)
    subscribers = messagebus.handle(
        commands.ListSubscribers(channel_name="general", author="john", text="Goodbye World"), uow=uow
    )
    assert subscribers == [{"bob", "alice"}]


def test_get_subscribers_errors_for_unknown_channel() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown channel"):
        messagebus.handle(
            commands.ListSubscribers(channel_name="general", author="john", text="Goodbye World"), uow=uow
        )


def test_can_unsubscribe() -> None:
    uow = FakeUnitOfWork()
    messagebus.handle(commands.Subscribe(channel_name="general", subscriber="bob", keyword="hello"), uow=uow)
    messagebus.handle(commands.Unsubscribe(channel_name="general", subscriber="bob", keyword="hello"), uow=uow)
    subscriptions = messagebus.handle(commands.ListSubscriptions(channel_name="general", subscriber="bob"), uow=uow)
    assert subscriptions == [set()]


def test_unsubscribe_errors_for_unknown_channel() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(ValueError, match="Unknown channel"):
        messagebus.handle(commands.Unsubscribe(channel_name="general", subscriber="bob", keyword="hello"), uow=uow)


def test_unsubscribe_errors_for_unknown_subscription() -> None:
    uow = FakeUnitOfWork()
    messagebus.handle(commands.Subscribe(channel_name="general", subscriber="john", keyword="hello"), uow=uow)
    with pytest.raises(ValueError, match="Unknown subscription"):
        messagebus.handle(commands.Unsubscribe(channel_name="general", subscriber="bob", keyword="hello"), uow=uow)
