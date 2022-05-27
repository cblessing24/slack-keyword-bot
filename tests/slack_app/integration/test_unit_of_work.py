from typing import Any

import pytest

from slack_app.service_layer.unit_of_work import SQLAlchemyUnitOfWork

from ..conftest import KeywordCreator


def test_can_insert_keyword(session_factory: Any, create_keyword: KeywordCreator) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    with uow:
        uow.keywords.add(create_keyword(channel_name="general", subscriber="bob", word="hello"))
        uow.commit()

    session = session_factory()
    assert list(session.execute("SELECT * FROM 'keyword'")) == [(1, "general", "bob", "hello", True)]


def test_rolls_back_changes_by_default(session_factory: Any, create_keyword: KeywordCreator) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    with uow:
        keyword = create_keyword()
        uow.keywords.add(keyword)

    session = session_factory()
    assert list(session.execute("SELECT * FROM 'keyword'")) == []


def test_rolls_back_on_error(session_factory: Any, create_keyword: KeywordCreator) -> None:
    class MyException(Exception):
        pass

    uow = SQLAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            keyword = create_keyword()
            uow.keywords.add(keyword)
            raise MyException()

    session = session_factory()
    assert list(session.execute("SELECT * FROM 'keyword'")) == []


def test_session_only_available_in_context(session_factory: Any) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    with pytest.raises(RuntimeError, match="not available outside of context"):
        _ = uow.session
