from dataclasses import dataclass
from typing import Callable

import pytest

from slack_app.adapters.notifications import SlackClient, SlackNotifications


class FakeSlackClient:
    @dataclass
    class Message:
        channel: str
        text: str

    def __init__(self) -> None:
        self.messages: list[FakeSlackClient.Message] = []

    def chat_postMessage(self, channel: str, text: str) -> None:
        self.messages.append(FakeSlackClient.Message(channel, text))


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


def test_can_respond(client_factory: Callable[[], SlackClient]) -> None:
    class FakeSlackRespond:
        def __init__(self) -> None:
            self.messages: list[str] = []

        def __call__(self, message: str) -> None:
            self.messages.append(message)

    notifications = SlackNotifications(client_factory)
    slack_respond = FakeSlackRespond()
    notifications.slack_respond = slack_respond
    notifications.respond(message="Hello, world!")
    assert slack_respond.messages == ["Hello, world!"]
