import logging

logging.basicConfig(level=logging.DEBUG)


from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

load_dotenv()

app = App()

notifications = {}


def create_notification(channel: str, user: str, keyword: str):
    pass


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("message")
def event_message(event, client):
    for keyword, user_id in notifications.items():
        if keyword in event["text"]:
            quoted = "> " + "\n> ".join(event["text"].split("\n"))
            text = f"<@{event['user']}> mentioned '{keyword}' in <#{event['channel']}>:\n{quoted}"
            client.chat_postMessage(channel=user_id, text=text)


@app.command("/notify")
def command_notify(ack, command, respond):
    ack()
    create_notification(channel=command["channel_id"], user=command["user_id"], keyword=command["text"])
    respond(f"You will be notified if '{command['text']}' is mentioned in <#{command['channel_id']}>!")


from flask import Flask, request

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)
