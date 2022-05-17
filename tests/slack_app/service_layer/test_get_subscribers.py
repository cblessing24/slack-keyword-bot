from slack_app.domain.model import Channel, Keyword, Message, Text, User, Word
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
    message = Message(channel=Channel("general"), user=User("john"), text=Text("Goodbye World"))
    subscribers = get_subscribers(repo, message)
    assert subscribers == {User("bob"), User("alice")}
