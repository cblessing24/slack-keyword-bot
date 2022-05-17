from sqlalchemy.orm import Session

from slack_app.model import Channel, Keyword, User, Word
from slack_app.repository import SQLAlchemyRepository


def test_can_add_keyword(session: Session) -> None:
    repo = SQLAlchemyRepository(session)
    repo.add(Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello")))
    session.commit()
    rows = list(session.execute("SELECT channel, user, word FROM keyword"))
    assert rows == [("general", "bob", "hello")]


def test_can_get_keyword(session: Session) -> None:
    session.execute("INSERT INTO keyword (channel, user, word) VALUES ('general', 'bob', 'hello')")
    repo = SQLAlchemyRepository(session)
    keywords = repo.get(channel=Channel("general"), user=User("bob"))
    assert keywords == [Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))]
