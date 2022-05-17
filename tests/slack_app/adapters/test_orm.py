from typing import Any

from slack_app.domain.model import Channel, Keyword, User, Word


def test_keyword_mapper_can_load_keywords(session: Any) -> None:
    session.execute(
        "INSERT INTO keyword (channel, user, word) VALUES "
        "('general', 'bob', 'hello'),"
        "('random', 'alice', 'tree'),"
        "('lunch', 'steven', 'chicken')"
    )
    expected = [
        Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello")),
        Keyword(channel=Channel("random"), user=User("alice"), word=Word("tree")),
        Keyword(channel=Channel("lunch"), user=User("steven"), word=Word("chicken")),
    ]
    assert session.query(Keyword).all() == expected


def test_keyword_mapper_can_save_keywords(session: Any) -> None:
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    session.add(keyword)
    session.commit()
    rows = list(session.execute("SELECT channel, user, word FROM keyword"))
    assert rows == [("general", "bob", "hello")]
