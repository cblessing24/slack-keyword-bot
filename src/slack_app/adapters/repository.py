from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from slack_app.domain.model import Channel, Keyword


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, keyword: Keyword) -> None:
        pass

    @abstractmethod
    def get(self, channel: Channel) -> list[Keyword]:
        pass


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, keyword: Keyword) -> None:
        self.session.add(keyword)

    def get(self, channel: Channel) -> list[Keyword]:
        return self.session.query(Keyword).filter_by(channel=channel).all()  # type: ignore[no-any-return]
