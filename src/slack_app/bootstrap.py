import functools
import inspect
from typing import Any, Mapping, Optional, cast

from .adapters import orm
from .adapters.notifications import AbstractNotifications
from .service_layer.handlers import COMMAND_HANDLERS, EVENT_HANDLERS, M, MessageHandler
from .service_layer.messagebus import MessageBus, U


def bootstrap(
    uow: U, *, start_mappers: bool = True, notifications: Optional[AbstractNotifications] = None
) -> MessageBus[U]:
    if start_mappers:
        orm.start_mappers()
    return cast(MessageBus[U], MessageBus(uow, event_handlers=EVENT_HANDLERS, command_handlers=COMMAND_HANDLERS))


def inject_dependencies(handler: MessageHandler[M], dependencies: Mapping[str, Any]) -> MessageHandler[M]:
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return functools.partial(handler, **deps)
