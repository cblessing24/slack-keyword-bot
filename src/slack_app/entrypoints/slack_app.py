from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, TypedDict

from dotenv import load_dotenv
from flask import Flask, request
from flask.wrappers import Response
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from ..adapters.orm import start_mappers
from ..service_layer.services import list_subscribers, list_subscriptions, subscribe, unsubscribe
from ..service_layer.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from slack_bolt.context.ack import Ack
    from slack_bolt.context.respond import Respond
    from slack_sdk.web.client import WebClient


class Command(TypedDict):
    channel_id: str
    user_id: str
    text: Optional[str]


class Event(TypedDict):
    user: str
    channel: str
    text: str


logging.basicConfig(level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING")))
load_dotenv()
start_mappers()

app = App()


@app.middleware
def log_request(logger: logging.Logger, body: Mapping[str, Any], next: Callable[[], None]) -> None:
    logger.debug(body)
    return next()


@app.event("message")
def event_message(logger: logging.Logger, event: Event, client: WebClient) -> None:
    try:
        subscribers = list_subscribers(
            SQLAlchemyUnitOfWork(), channel_name=event["channel"], author=event["user"], text=event["text"]
        )
    except ValueError as e:
        logger.warning(e)
        return
    for subscriber in subscribers:
        quoted = "> " + "\n> ".join(event["text"].split("\n"))
        text = f"<@{event['user']}> mentioned a keyword in <#{event['channel']}>:\n{quoted}"
        client.chat_postMessage(channel=subscriber, text=text)


@app.command("/keyword-subscribe")
def command_keyword_subscribe(ack: Ack, command: Command, respond: Respond) -> None:
    ack()
    keyword = command.get("text") or ""
    subscribe(
        SQLAlchemyUnitOfWork(),
        channel_name=command["channel_id"],
        subscriber=command["user_id"],
        keyword=keyword,
    )
    respond(f"You will be notified if '{keyword}' is mentioned in <#{command['channel_id']}>!")


@app.command("/keyword-list")
def command_keyword_list(ack: Ack, command: Command, respond: Respond) -> None:
    ack()
    no_subscriptions_msg = f"You are not subscribed to any keywords in <#{command['channel_id']}>."
    try:
        subscriptions = list_subscriptions(
            SQLAlchemyUnitOfWork(), channel_name=command["channel_id"], subscriber=command["user_id"]
        )
    except ValueError:
        respond(no_subscriptions_msg)
        return
    if not subscriptions:
        respond(no_subscriptions_msg)
        return
    kewywords_text = "\n".join(f"    - '{k}'" for k in subscriptions)
    respond(f"Your subscriptions in this channel:\n{kewywords_text}")


@app.command("/keyword-unsubscribe")
def command_keyword_unsubscribe(ack: Ack, command: Command, respond: Respond) -> None:
    ack()
    keyword = command.get("text") or ""
    try:
        unsubscribe(
            SQLAlchemyUnitOfWork(),
            channel_name=command["channel_id"],
            subscriber=command["user_id"],
            keyword=keyword,
        )
    except ValueError:
        respond(f"You are not subscribed to '{keyword}' in <#{command['channel_id']}>!")
        return
    respond(f"You will no longer be notified if '{keyword}' is mentioned in <#{command['channel_id']}>!")


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events() -> Response:
    return handler.handle(request)  # type: ignore[no-any-return]
