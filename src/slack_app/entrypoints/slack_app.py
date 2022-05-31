from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Mapping

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

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
start_mappers()

app = App()


@app.middleware
def log_request(logger: logging.Logger, body: Mapping[str, Any], next: Callable[[], None]) -> None:
    logger.debug(body)
    return next()


@app.event("message")
def event_message(event: Mapping[str, Any], client: WebClient) -> None:
    for subscriber in list_subscribers(
        SQLAlchemyUnitOfWork(), channel_name=event["channel"], author=event["user"], text=event["text"]
    ):
        quoted = "> " + "\n> ".join(event["text"].split("\n"))
        text = f"<@{event['user']}> mentioned a keyword in <#{event['channel']}>:\n{quoted}"
        client.chat_postMessage(channel=subscriber, text=text)


@app.command("/notify-create")
def command_notify_create(ack: Ack, command: Mapping[str, Any], respond: Respond) -> None:
    ack()
    subscribe(
        SQLAlchemyUnitOfWork(), channel_name=command["channel_id"], subscriber=command["user_id"], word=command["text"]
    )
    respond(f"You will be notified if '{command['text']}' is mentioned in <#{command['channel_id']}>!")


@app.command("/notify-list")
def command_notify_list(ack: Ack, command: Mapping[str, Any], respond: Respond) -> None:
    ack()
    subscriptions = list_subscriptions(
        SQLAlchemyUnitOfWork(), channel_name=command["channel_id"], subscriber=command["user_id"]
    )
    if not subscriptions:
        respond("You have no subscriptions in this channel.")
        return
    kewywords_text = "\n".join(f"    - {k}" for k in subscriptions)
    respond(f"Your subscriptions in this channel:\n{kewywords_text}")


@app.command("/notify-remove")
def command_notify_remove(ack: Ack, command: Mapping[str, Any], respond: Respond) -> None:
    ack()
    try:
        unsubscribe(
            SQLAlchemyUnitOfWork(),
            channel_name=command["channel_id"],
            subscriber=command["user_id"],
            word=command["text"],
        )
    except ValueError:
        respond(
            f"Can not remove subscription: "
            "You are not subscribed to '{command['text']}' in <#{command['channel_id']}>!"
        )
        return
    respond(f"You will no longer be notified if '{command['text']}' is mentioned in <#{command['channel_id']}>!")


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events() -> Response:
    return handler.handle(request)  # type: ignore[no-any-return]
