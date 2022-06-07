from typing import Optional

from slack_app.adapters.repository import AbstractRepository
from slack_app.domain.model import Channel, ChannelName


class FakeRepository(AbstractRepository):
    def __init__(self, channels: Optional[set[Channel]] = None) -> None:
        super().__init__()
        self.channels = channels if channels is not None else set()

    def _add(self, channel: Channel) -> None:
        self.channels.add(channel)

    def _get(self, channel_name: ChannelName) -> Channel | None:
        try:
            return next(c for c in self.channels if c.channel_name == channel_name)
        except StopIteration:
            return None
