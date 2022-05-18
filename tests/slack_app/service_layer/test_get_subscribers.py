from slack_app.domain.model import Channel, Keyword, User, Word
from slack_app.service_layer.services import get_subscribers

from .conftest import RepositoryCreator


def test_subscribers_are_returned(create_repo: RepositoryCreator) -> None:
    repo = create_repo(
        keywords={
            Keyword(channel=Channel("general"), user=User("bob"), word=Word("Hello")),
            Keyword(channel=Channel("general"), user=User("bob"), word=Word("World")),
            Keyword(channel=Channel("general"), user=User("alice"), word=Word("World")),
            Keyword(channel=Channel("random"), user=User("alice"), word=Word("World")),
        }
    )
    subscribers = get_subscribers(repo, channel="general", user="john", text="Goddbye World")
    assert subscribers == {"bob", "alice"}
