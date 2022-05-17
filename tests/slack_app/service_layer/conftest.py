from typing import Iterable, List, Optional, Protocol, Set

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, Keyword, User


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
