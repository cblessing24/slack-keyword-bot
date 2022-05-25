from typing import Any

from slack_app.domain.model import Keyword

from ..conftest import KeywordCreator


def test_keyword_mapper_can_load_keywords(session: Any, create_keyword: KeywordCreator) -> None:
    session.execute(
        "INSERT INTO keyword (channel, subscriber, word, active) VALUES "
        "('general', 'bob', 'hello', 1),"
        "('random', 'alice', 'tree', 1),"
        "('lunch', 'steven', 'chicken', 0)"
    )
    expected = [
        create_keyword(channel="general", subscriber="bob", word="hello", active=True),
        create_keyword(channel="random", subscriber="alice", word="tree", active=True),
        create_keyword(channel="lunch", subscriber="steven", word="chicken", active=False),
    ]
    assert session.query(Keyword).all() == expected


def test_keyword_mapper_can_save_keywords(session: Any, create_keyword: KeywordCreator) -> None:
    keyword = create_keyword(channel="general", subscriber="bob", word="hello", active=True)
    session.add(keyword)
    session.commit()
    rows = list(session.execute("SELECT channel, subscriber, word, active FROM keyword"))
    assert rows == [("general", "bob", "hello", 1)]
