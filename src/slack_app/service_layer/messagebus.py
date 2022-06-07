from typing import Any, Generic, Protocol, Type, TypeVar, cast

from ..domain import events
from . import handlers, unit_of_work


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]) -> list[Any]:
    results: list[Any] = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results


E = TypeVar("E", bound=events.Event, contravariant=True)


class Handler(Protocol, Generic[E]):
    def __call__(self, event: E, uow: unit_of_work.AbstractUnitOfWork[unit_of_work.R]) -> Any:
        ...


class HandlerMap(Protocol):
    def __getitem__(self, event: Type[E]) -> list[Handler[E]]:
        """Returns a list of callables that handle the given event."""


HANDLERS = cast(
    HandlerMap,
    {
        events.AlreadySubscribed: [],
        events.Subscribed: [handlers.subscribe],
        events.SubscriptionsListRequired: [handlers.list_subscriptions],
        events.SubscriberListRequired: [handlers.list_subscribers],
        events.Unsubscribed: [handlers.unsubscribe],
    },
)
