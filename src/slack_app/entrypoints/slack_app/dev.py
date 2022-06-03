import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from . import configure_app

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
configure_app(app)
SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()  # type: ignore[no-untyped-call]
