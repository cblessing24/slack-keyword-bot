from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from slack_app.domain.model import Channel, ChannelName


class AbstractRepository(ABC):
    def __init__(self) -> None:
        self.seen: set[Channel] = set()

    def add(self, channel: Channel) -> None:
        self._add(channel)
        self.seen.add(channel)

    def get(self, channel_name: ChannelName) -> Channel | None:
        channel = self._get(channel_name)
        if channel:
            self.seen.add(channel)
        return channel

    @abstractmethod
    def _add(self, channel: Channel) -> None:
        """Add a channel to the repository."""

    @abstractmethod
    def _get(self, channel_name: ChannelName) -> Channel | None:
        """Get a channel from the repository."""


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def _add(self, channel: Channel) -> None:
        self.session.add(channel)

    def _get(self, channel_name: ChannelName) -> Channel | None:
        return self.session.query(Channel).filter_by(channel_name=channel_name).first()  # type: ignore[no-any-return]
