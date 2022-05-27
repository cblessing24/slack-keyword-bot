from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from slack_app.domain.model import Channel, ChannelName


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, channel: Channel) -> None:
        """Add a channel to the repository."""

    @abstractmethod
    def get(self, channel_name: ChannelName) -> Channel | None:
        """Get a channel from the repository."""


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, channel: Channel) -> None:
        self.session.add(channel)

    def get(self, channel_name: ChannelName) -> Channel | None:
        return self.session.query(Channel).filter_by(channel_name=channel_name).first()  # type: ignore[no-any-return]
