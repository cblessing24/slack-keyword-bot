from slack_app.service_layer.services import add_keyword, get_subscribers

from .conftest import FakeRepositoryCreator, FakeSession


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
