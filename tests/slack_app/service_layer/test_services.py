from slack_app.service_layer.services import add_keyword, list_keywords

from .conftest import FakeRepositoryCreator


class FakeSession:
    committed = False

    def commit(self) -> None:
        self.committed = True


def test_keyword_gets_added(create_repo: FakeRepositoryCreator) -> None:
    repo = create_repo()
    session = FakeSession()
    add_keyword(repo, session, channel="general", user="bob", word="hello")
    keywords = list_keywords(repo, channel="general", user="bob")
    assert keywords == {"hello"}


def test_added_keyword_gets_committed(create_repo: FakeRepositoryCreator) -> None:
    session = FakeSession()
    add_keyword(create_repo(), session, channel="general", user="bob", word="hello")
    assert session.committed
