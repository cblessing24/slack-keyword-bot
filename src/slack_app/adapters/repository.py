from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from slack_app.domain.model import ChannelName, Keyword


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, keyword: Keyword) -> None:
        """Add a keyword to the repository."""

    @abstractmethod
    def get(self, channel_name: ChannelName) -> list[Keyword]:
        """Get all keywords for a channel."""


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, keyword: Keyword) -> None:
        self.session.add(keyword)

    def get(self, channel_name: ChannelName) -> list[Keyword]:
        return self.session.query(Keyword).filter_by(channel_name=channel_name).all()  # type: ignore[no-any-return]
