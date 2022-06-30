from abc import ABC, abstractmethod
from typing import Callable, Protocol

from slack_sdk import WebClient

from .. import config


class AbstractNotifications(ABC):
    @abstractmethod
    def send(self, channel: str, message: str) -> None:
        pass

    @abstractmethod
    def respond(self, message: str) -> None:
        pass


class SlackClient(Protocol):
    def chat_postMessage(self, *, channel: str, text: str) -> None:
        ...


def create_slack_client() -> WebClient:
    return WebClient(token=config.get_slack_bot_token())


DEFAULT_CLIENT_FACTORY = create_slack_client


class SlackRespond(Protocol):
    def __call__(self, message: str) -> None:
        ...


class SlackNotifications(AbstractNotifications):
    slack_respond: SlackRespond

    def __init__(self, client_factory: Callable[[], SlackClient] = DEFAULT_CLIENT_FACTORY) -> None:
        self.client = client_factory()

    def send(self, channel: str, message: str) -> None:
        self.client.chat_postMessage(channel=channel, text=message)

    def respond(self, message: str) -> None:
        self.slack_respond(message)
