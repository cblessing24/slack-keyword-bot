from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, TypedDict

from slack_bolt import App

from ...adapters.notifications import SlackNotifications, SlackRespond
from ...bootstrap import bootstrap
from ...domain import commands
from ...service_layer.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from slack_bolt.context.ack import Ack
    from slack_bolt.context.respond import Respond
    from slack_sdk.web.client import WebClient


@dataclass(frozen=True)
class Component:
    type: str
    function: Any

    def register(self, app: App) -> None:
        getattr(app, self.type)(self.function)


@dataclass(frozen=True)
class Listener(Component):
    args: Optional[list[Any]] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)

    def register(self, app: App) -> None:
        getattr(app, self.type)(*self.args, **self.kwargs)(self.function)


class Command(TypedDict):
    channel_id: str
    user_id: str
    text: Optional[str]


class Message(TypedDict):
    user: str
    channel: str
    text: str


class BotMessage(TypedDict):
    bot_id: str
    channel: str
    text: str


def create_respond_closure(respond: Respond) -> SlackRespond:
    def respond_closure(text: str) -> None:
        respond(text)

    return staticmethod(respond_closure)


bus = bootstrap(SQLAlchemyUnitOfWork())
components: list[Component] = []


def log_request(logger: logging.Logger, body: Mapping[str, Any], next: Callable[[], None]) -> None:
    logger.debug(body)
    return next()


components.append(Component("middleware", log_request))


def event_bot_message(event: BotMessage, client: WebClient) -> None:
    bot_name = client.bots_info(bot=event["bot_id"])["bot"]["name"]
    SlackNotifications.replacements[event["bot_id"]] = bot_name
    bus.handle(
        commands.FindMentions(channel_name=event["channel"], author=event["bot_id"], text=event["text"]),
    )


components.append(Listener("event", event_bot_message, args=[{"type": "message", "subtype": "bot_message"}]))


def event_message(event: Message) -> None:
    bus.handle(
        commands.FindMentions(channel_name=event["channel"], author=event["user"], text=event["text"]),
    )


components.append(Listener("event", event_message, args=["message"]))


def command_keyword_subscribe(ack: Ack, command: Command, respond: Respond) -> None:
    ack()
    keyword = command.get("text") or ""
    SlackNotifications.slack_respond = create_respond_closure(respond)
    bus.handle(
        commands.Subscribe(channel_name=command["channel_id"], subscriber=command["user_id"], keyword=keyword),
    )


components.append(Listener("command", command_keyword_subscribe, args=["/keyword-subscribe"]))


def command_keyword_list(ack: Ack, command: Command, respond: Respond) -> None:
    ack()
    no_subscriptions_msg = f"You are not subscribed to any keywords in <#{command['channel_id']}>."
    try:
        subscriptions = bus.handle(
            commands.ListSubscriptions(channel_name=command["channel_id"], subscriber=command["user_id"]),
        )[0]
    except ValueError:
        respond(no_subscriptions_msg)
        return
    if not subscriptions:
        respond(no_subscriptions_msg)
        return
    kewywords_text = "\n".join(f"    - '{k}'" for k in subscriptions)
    respond(f"Your subscriptions in this channel:\n{kewywords_text}")


components.append(Listener("command", command_keyword_list, args=["/keyword-list"]))


def command_keyword_unsubscribe(ack: Ack, command: Command, respond: Respond) -> None:
    ack()
    keyword = command.get("text") or ""
    SlackNotifications.slack_respond = create_respond_closure(respond)
    bus.handle(
        commands.Unsubscribe(channel_name=command["channel_id"], subscriber=command["user_id"], keyword=keyword),
    )


components.append(Listener("command", command_keyword_unsubscribe, args=["/keyword-unsubscribe"]))
