from flask import Flask, request
from flask.wrappers import Response
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from . import configure_app

flask_app = Flask(__name__)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events() -> Response:
    return handler.handle(request)  # type: ignore[no-any-return]


app = App()
configure_app(app)
handler = SlackRequestHandler(app)
