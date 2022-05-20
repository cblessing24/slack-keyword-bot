from slack_app.service_layer.services import add_keyword, get_subscribers, list_keywords
from slack_app.service_layer.unit_of_work import AbstractUnitOfWork

from .conftest import FakeRepository


class FakeUnitOfWork(AbstractUnitOfWork[FakeRepository]):
    def __init__(self) -> None:
        self.committed = False
        self.keywords = FakeRepository()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_keyword_gets_added() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel="general", user="bob", word="hello")
    keywords = list_keywords(uow, channel="general", subscriber="bob")
    assert keywords == {"hello"}


def test_added_keyword_gets_committed() -> None:
    uow = FakeUnitOfWork()
    add_keyword(uow, channel="general", user="bob", word="hello")
    assert issubclass(FakeUnitOfWork, AbstractUnitOfWork)
    assert uow.committed


def test_subscribers_are_returned() -> None:
    uow = FakeUnitOfWork()
    in_keyword = ("general", "bob", "World")
    out_keyword = ("general", "alice", "World")
    author_keyword = ("general", "john", "Goodbye")
    keywords = [in_keyword, out_keyword, author_keyword]
    for keyword in keywords:
        add_keyword(uow, *keyword)
    subscribers = get_subscribers(uow, channel="general", author="john", text="Goodbye World")
    assert subscribers == {"bob", "alice"}
