from typing import Any

from slack_app.model import Keyword


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
