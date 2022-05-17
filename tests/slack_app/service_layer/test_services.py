from typing import Iterable, List, Optional, Protocol, Set

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, Keyword, User, Word
from slack_app.service_layer.services import add_keyword


class FakeRepository(AbstractRepository):
    def __init__(self, keywords: Set[Keyword]) -> None:
        self.keywords = keywords

    def add(self, keyword: Keyword) -> None:
        self.keywords.add(keyword)

    def get(self, channel: Channel, user: User) -> List[Keyword]:
        return [k for k in self.keywords if k.channel == channel and k.user == user]


class RepositoryCreator(Protocol):
    def __call__(self, keywords: Optional[Set[Keyword]] = None) -> FakeRepository:
        ...


@pytest.fixture
def create_repo() -> RepositoryCreator:
    def create(keywords: Optional[Iterable[Keyword]] = None) -> FakeRepository:
        return FakeRepository(set(keywords) if keywords else set())

    return create


class FakeSession:
    committed = False

    def commit(self) -> None:
        self.committed = True


def test_keyword_gets_added_to_repository(create_repo: RepositoryCreator) -> None:
    repo = create_repo()
    session = FakeSession()
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    add_keyword(repo, session, keyword)
    assert repo.get(keyword.channel, keyword.user) == [keyword]


def test_added_keyword_gets_committed(create_repo: RepositoryCreator) -> None:
    session = FakeSession()
    keyword = Keyword(channel=Channel("general"), user=User("bob"), word=Word("hello"))
    add_keyword(create_repo(), session, keyword)
    assert session.committed
