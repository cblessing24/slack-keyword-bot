from typing import Any

from slack_app.domain.model import Keyword

from ..conftest import KeywordCreator


def test_keyword_mapper_can_load_keywords(session: Any, create_keyword: KeywordCreator) -> None:
    session.execute(
        "INSERT INTO keyword (channel, subscriber, word) VALUES "
        "('general', 'bob', 'hello'),"
        "('random', 'alice', 'tree'),"
        "('lunch', 'steven', 'chicken')"
    )
    expected = [
        create_keyword(channel="general", subscriber="bob", word="hello"),
        create_keyword(channel="random", subscriber="alice", word="tree"),
        create_keyword(channel="lunch", subscriber="steven", word="chicken"),
    ]
    assert session.query(Keyword).all() == expected


def test_keyword_mapper_can_save_keywords(session: Any, create_keyword: KeywordCreator) -> None:
    keyword = create_keyword(channel="general", subscriber="bob", word="hello")
    session.add(keyword)
    session.commit()
    rows = list(session.execute("SELECT channel, subscriber, word FROM keyword"))
    assert rows == [("general", "bob", "hello")]
