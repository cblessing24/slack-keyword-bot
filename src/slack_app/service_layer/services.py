from sqlalchemy.orm.session import Session

from ..adapters.repository import AbstractRepository
from ..domain.model import Keyword


def add_keyword(repo: AbstractRepository, session: Session, keyword: Keyword) -> None:
    repo.add(keyword)
    session.commit()
