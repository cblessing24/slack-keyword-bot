from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Generic, Optional, Type, TypeVar

from ..adapters.repository import AbstractRepository, SQLAlchemyRepository

R = TypeVar("R", bound="AbstractRepository")


class AbstractUnitOfWork(ABC, Generic[R]):
    keywords: R
    U = TypeVar("U", bound="AbstractUnitOfWork[R]")  # pyright: ignore

    def __enter__(self: U) -> U:
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        self.rollback()

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass


class SQLAlchemyUnitOfWork(AbstractUnitOfWork[SQLAlchemyRepository]):
    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory
        self._session: Optional[Any] = None

    @property
    def session(self) -> Any:
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        return self._session

    def __enter__(self) -> SQLAlchemyUnitOfWork:
        session = self.session_factory()
        self.keywords = SQLAlchemyRepository(session)
        self._session = session
        return super().__enter__()

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        super().__exit__(exc_type, exc, traceback)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
