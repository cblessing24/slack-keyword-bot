from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator
from unittest import mock

import pytest
from sqlalchemy.orm import clear_mappers

from slack_app import bootstrap, views
from slack_app.domain import commands
from slack_app.service_layer.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from slack_app.service_layer.messagebus import MessageBus


@pytest.fixture
def sqlite_bus(session_factory: Any) -> Generator[MessageBus[SQLAlchemyUnitOfWork], None, None]:
    bus = bootstrap.bootstrap(
        SQLAlchemyUnitOfWork(session_factory),
        start_mappers=True,
        notifications=mock.Mock(),
    )
    yield bus
    clear_mappers()


def test_subscriptions_view(sqlite_bus: MessageBus[SQLAlchemyUnitOfWork]) -> None:
    sqlite_bus.handle(commands.Subscribe("#general", "bob", "hello"))
    sqlite_bus.handle(commands.Subscribe("#general", "bob", "world"))
    sqlite_bus.handle(commands.Subscribe("#general", "bob", "goodbye"))
    sqlite_bus.handle(commands.Subscribe("#general", "john", "hello"))
    sqlite_bus.handle(commands.Subscribe("#random", "bob", "hello"))
    sqlite_bus.handle(commands.Subscribe("#random", "john", "hello"))
    sqlite_bus.handle(commands.Unsubscribe("#general", "bob", "goodbye"))

    assert views.keywords("#general", "bob", sqlite_bus.uow) == ["hello", "world"]
