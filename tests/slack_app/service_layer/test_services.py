from slack_app.service_layer.services import add_keyword, get_subscribers, list_keywords

from .conftest import FakeRepositoryCreator, FakeSession


def test_keyword_gets_added(create_repo: FakeRepositoryCreator, session: FakeSession) -> None:
    repo = create_repo()
    add_keyword(repo, session, channel="general", user="bob", word="hello")
    keywords = list_keywords(repo, channel="general", user="bob")
    assert keywords == {"hello"}


def test_added_keyword_gets_committed(create_repo: FakeRepositoryCreator, session: FakeSession) -> None:
    add_keyword(create_repo(), session, channel="general", user="bob", word="hello")
    assert session.committed


def test_subscribers_are_returned(create_repo: FakeRepositoryCreator, session: FakeSession) -> None:
    repo = create_repo()
    keywords = [
        ("general", "bob", "Hello"),
        ("general", "bob", "World"),
        ("general", "alice", "World"),
        ("random", "alice", "World"),
    ]
    for keyword in keywords:
        add_keyword(repo, session, *keyword)
    subscribers = get_subscribers(repo, channel="general", user="john", text="Goddbye World")
    assert subscribers == {"bob", "alice"}
