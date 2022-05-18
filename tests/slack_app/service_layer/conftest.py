from __future__ import annotations

from typing import Iterable, List, Optional, Set, Tuple

import pytest

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, Keyword, User, Word


class FakeRepository(AbstractRepository):
    def __init__(self, keywords: Optional[Set[Keyword]] = None) -> None:
        self.keywords = keywords if keywords is not None else set()

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
                for channel, user, word in keywords
            }
        )


class FakeRepositoryCreator:
    def __call__(self) -> FakeRepository:
        return FakeRepository()

    def for_keywords(self, keywords: Iterable[Tuple[str, str, str]]) -> FakeRepository:
        return FakeRepository.for_keywords(keywords)


@pytest.fixture
def create_repo() -> FakeRepositoryCreator:
    return FakeRepositoryCreator()


class FakeSession:
    committed = False

    def commit(self) -> None:
        self.committed = True


@pytest.fixture
def session() -> FakeSession:
    return FakeSession()
