from typing import Any

import pytest

from slack_app.domain.model import Channel, ChannelName
from slack_app.service_layer.unit_of_work import SQLAlchemyUnitOfWork


def test_can_add_channel(session_factory: Any) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    with uow:
        uow.channels.add(Channel(ChannelName("general")))
        uow.commit()

    session = session_factory()
    assert list(session.execute("SELECT * FROM 'channel'")) == [("general",)]


def test_rolls_back_changes_by_default(session_factory: Any) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    with uow:
        uow.channels.add(Channel(ChannelName("general")))

    session = session_factory()
    assert list(session.execute("SELECT * FROM 'channel'")) == []


def test_rolls_back_on_error(session_factory: Any) -> None:
    class MyException(Exception):
        pass

    uow = SQLAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            uow.channels.add(Channel(ChannelName("general")))
            raise MyException()

    session = session_factory()
    assert list(session.execute("SELECT * FROM 'channel'")) == []


def test_session_only_available_in_context(session_factory: Any) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    with pytest.raises(RuntimeError, match="not available outside of context"):
        _ = uow.session
