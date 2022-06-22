from dataclasses import dataclass
from typing import Callable, Optional

import pytest

from slack_app.adapters.notifications import SlackClient, SlackNotifications


class FakeSlackClient:
    @dataclass
    class Message:
        channel: str
        text: str
        user: Optional[str] = None

    def __init__(self) -> None:
        self.messages: list[FakeSlackClient.Message] = []

    def chat_postMessage(self, channel: str, text: str) -> None:
        self.messages.append(FakeSlackClient.Message(channel, text))

    def chat_postEphemeral(self, channel: str, text: str, user: str) -> None:
        self.messages.append(FakeSlackClient.Message(channel, text, user))


@pytest.fixture
def slack_client() -> FakeSlackClient:
    return FakeSlackClient()


@pytest.fixture
def client_factory(slack_client: FakeSlackClient) -> Callable[[], FakeSlackClient]:
    def _client_factory() -> FakeSlackClient:
        return slack_client

    return _client_factory


def test_can_send_message(slack_client: FakeSlackClient, client_factory: Callable[[], SlackClient]) -> None:
    notifications = SlackNotifications(client_factory)
    notifications.send(channel="#general", message="Hello, world!")
    assert slack_client.messages == [FakeSlackClient.Message("#general", "Hello, world!")]


def test_can_respond(slack_client: FakeSlackClient, client_factory: Callable[[], SlackClient]) -> None:
    notifications = SlackNotifications(client_factory)
    notifications.respond(channel="#general", message="Hello, world!", recipient="U12345")
    assert slack_client.messages == [FakeSlackClient.Message("#general", "Hello, world!", user="U12345")]
