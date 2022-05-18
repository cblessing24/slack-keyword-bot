from slack_app.service_layer.services import add_keyword, list_keywords

from .conftest import FakeRepositoryCreator, FakeSession


def test_keyword_gets_added(create_repo: FakeRepositoryCreator, session: FakeSession) -> None:
    repo = create_repo()
    add_keyword(repo, session, channel="general", user="bob", word="hello")
    keywords = list_keywords(repo, channel="general", user="bob")
    assert keywords == {"hello"}


def test_added_keyword_gets_committed(create_repo: FakeRepositoryCreator, session: FakeSession) -> None:
    add_keyword(create_repo(), session, channel="general", user="bob", word="hello")
    assert session.committed
