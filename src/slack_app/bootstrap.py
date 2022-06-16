from typing import Optional, cast

from .adapters import orm
from .adapters.notifications import AbstractNotifications
from .service_layer.handlers import COMMAND_HANDLERS, EVENT_HANDLERS
from .service_layer.messagebus import MessageBus, U


def bootstrap(
    uow: U, *, start_mappers: bool = True, notifications: Optional[AbstractNotifications] = None
) -> MessageBus[U]:
    if start_mappers:
        orm.start_mappers()
    return cast(MessageBus[U], MessageBus(uow, event_handlers=EVENT_HANDLERS, command_handlers=COMMAND_HANDLERS))
