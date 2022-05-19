from typing import Any

from slack_app.domain.model import Channel, Keyword, User, Word


def test_keyword_mapper_can_load_keywords(session: Any) -> None:
    session.execute(
        "INSERT INTO keyword (channel, subscriber, word) VALUES "
        "('general', 'bob', 'hello'),"
        "('random', 'alice', 'tree'),"
        "('lunch', 'steven', 'chicken')"
    )
    expected = [
        Keyword(channel=Channel("general"), subscriber=User("bob"), word=Word("hello")),
        Keyword(channel=Channel("random"), subscriber=User("alice"), word=Word("tree")),
        Keyword(channel=Channel("lunch"), subscriber=User("steven"), word=Word("chicken")),
    ]
    assert session.query(Keyword).all() == expected


def test_keyword_mapper_can_save_keywords(session: Any) -> None:
    keyword = Keyword(channel=Channel("general"), subscriber=User("bob"), word=Word("hello"))
    session.add(keyword)
    session.commit()
    rows = list(session.execute("SELECT channel, subscriber, word FROM keyword"))
    assert rows == [("general", "bob", "hello")]
