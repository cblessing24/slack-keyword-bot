from slack_app.domain.model import Channel, Keyword, User, Word
from slack_app.service_layer.services import add_keyword

from .conftest import RepositoryCreator


class FakeSession:
    committed = False

    def commit(self) -> None:
        self.committed = True


def test_keyword_gets_added_to_repository(create_repo: RepositoryCreator) -> None:
    repo = create_repo()
    session = FakeSession()
    add_keyword(repo, session, channel="general", user="bob", word="hello")
    assert repo.get(Channel("general")) == [Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))]


def test_added_keyword_gets_committed(create_repo: RepositoryCreator) -> None:
    session = FakeSession()
    add_keyword(create_repo(), session, channel="general", user="bob", word="hello")
    assert session.committed
