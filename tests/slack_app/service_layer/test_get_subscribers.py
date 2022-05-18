from slack_app.service_layer.services import get_subscribers

from .conftest import FakeRepositoryCreator


def test_subscribers_are_returned(create_repo: FakeRepositoryCreator) -> None:
    repo = create_repo.for_keywords(
        [
            ("general", "bob", "Hello"),
            ("general", "bob", "World"),
            ("general", "alice", "World"),
            ("random", "alice", "World"),
        ]
    )
    subscribers = get_subscribers(repo, channel="general", user="john", text="Goddbye World")
    assert subscribers == {"bob", "alice"}
