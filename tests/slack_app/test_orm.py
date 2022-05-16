from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from slack_app.model import Keyword
from slack_app.orm import metadata, start_mappers


@pytest.fixture  # type: ignore[misc]
def in_memory_db() -> Any:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture  # type: ignore[misc]
def session(in_memory_db: Any) -> Any:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def test_keyword_mapper_can_load_keywords(session: Any) -> None:
    session.execute(
        "INSERT INTO keyword (channel, user, word) VALUES "
        "('general', 'bob', 'hello'),"
        "('random', 'alice', 'tree'),"
        "('lunch', 'steven', 'chicken')"
    )
    expected = [
        Keyword(channel="general", user="bob", word="hello"),
        Keyword(channel="random", user="alice", word="tree"),
        Keyword(channel="lunch", user="steven", word="chicken"),
    ]
    assert session.query(Keyword).all() == expected


def test_keyword_mapper_can_save_keywords(session: Any) -> None:
    keyword = Keyword(channel="general", user="bob", word="hello")
    session.add(keyword)
    session.commit()
    rows = list(session.execute("SELECT channel, user, word FROM keyword"))
    assert rows == [("general", "bob", "hello")]
