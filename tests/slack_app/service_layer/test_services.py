from typing import Iterable, List, Optional

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, Keyword, User, Word
from slack_app.service_layer.services import add_keyword


class FakeRepository(AbstractRepository):
    def __init__(self, keywords: Optional[Iterable[Keyword]] = None) -> None:
        self.keywords = set(keywords) if keywords else set()

    def add(self, keyword: Keyword) -> None:
        self.keywords.add(keyword)

    def get(self, channel: Channel, user: User) -> List[Keyword]:
        return [k for k in self.keywords if k.channel == channel and k.user == user]


class FakeSession:
    committed = False

    def commit(self) -> None:
        self.committed = True


def test_keyword_gets_added_to_repository() -> None:
    repo = FakeRepository()
    session = FakeSession()
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    add_keyword(repo, session, keyword)
    assert repo.get(keyword.channel, keyword.user) == [keyword]


def test_added_keyword_gets_committed() -> None:
    repo = FakeRepository()
    session = FakeSession()
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    add_keyword(repo, session, keyword)
    assert session.committed
