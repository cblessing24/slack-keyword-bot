from __future__ import annotations

from typing import Iterable, List, Optional, Protocol, Set, Tuple

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, Keyword, User, Word


class FakeRepository(AbstractRepository):
    def __init__(self, keywords: Set[Keyword]) -> None:
        self.keywords = keywords

    def add(self, keyword: Keyword) -> None:
        self.keywords.add(keyword)

    def get(self, channel: Channel) -> List[Keyword]:
        return [k for k in self.keywords if k.channel == channel]

    @staticmethod
    def for_keywords(keywords: Iterable[Tuple[str, str, str]]) -> FakeRepository:
        return FakeRepository(
            {
                Keyword(
                    channel=Channel(channel),
                    user=User(user),
                    word=Word(word),
                )
                for channel, word, user in keywords
            }
        )


class RepositoryCreator(Protocol):
    def __call__(self, keywords: Optional[Set[Keyword]] = None) -> FakeRepository:
        ...


@pytest.fixture
def create_repo() -> RepositoryCreator:
    def create(keywords: Optional[Iterable[Keyword]] = None) -> FakeRepository:
        return FakeRepository(set(keywords) if keywords else set())

    return create
