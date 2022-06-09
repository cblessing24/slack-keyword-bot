import logging
import os

from dotenv import load_dotenv
from slack_bolt import App

from .components import components

logging.basicConfig(level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING")))
load_dotenv()


def configure_app(app: App) -> None:
    for component in components:
        component.register(app)
