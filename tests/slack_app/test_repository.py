from sqlalchemy.orm import Session

from slack_app.model import Keyword
from slack_app.repository import SQLAlchemyRepository


def test_can_add_keyword(session: Session) -> None:
    repo = SQLAlchemyRepository(session)
    repo.add(Keyword("general", "bob", "hello"))
    session.commit()
    rows = list(session.execute("SELECT channel, user, word FROM keyword"))
    assert rows == [("general", "bob", "hello")]


def test_can_get_keyword(session: Session) -> None:
    session.execute("INSERT INTO keyword (channel, user, word) VALUES ('general', 'bob', 'hello')")
    repo = SQLAlchemyRepository(session)
    keywords = repo.get("general", "bob")
    assert keywords == [Keyword("general", "bob", "hello")]
