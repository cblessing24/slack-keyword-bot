from typing import Callable, Protocol, Type, TypeVar, cast

from ..adapters import email
from ..domain import events


def handle(event: events.Event) -> None:
    for handler in HANDLERS[type(event)]:
        handler(event)


def send_already_subscribed_notification(event: events.AlreadySubscribed) -> None:
    email.send_mail(
        f"Hi {event.subscription.subscriber}, you are already subscribed "
        f"to '{event.subscription.keyword}' in #{event.subscription.channel_name}!"
    )


E = TypeVar("E", bound=events.Event)


class Handlers(Protocol):
    def __getitem__(self, event: Type[E]) -> list[Callable[[E], None]]:
        """Returns a list of callables that handle the given event."""


HANDLERS = cast(Handlers, {events.AlreadySubscribed: [send_already_subscribed_notification]})
