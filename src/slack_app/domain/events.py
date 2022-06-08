from __future__ import annotations

from dataclasses import dataclass

from . import model


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class AlreadySubscribed(Event):
    subscription: model.Subscription
