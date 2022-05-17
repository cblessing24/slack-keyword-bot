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
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    add_keyword(repo, session, keyword)
    assert repo.get(keyword.channel) == [keyword]


def test_added_keyword_gets_committed(create_repo: RepositoryCreator) -> None:
    session = FakeSession()
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    add_keyword(create_repo(), session, keyword)
    assert session.committed
