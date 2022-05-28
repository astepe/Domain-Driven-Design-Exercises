import abc

from requests import session

from allocation import config
from allocation.adapters import repository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(config.get_postgres_uri()))


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def commit(self):
        self._session.commit()

    def __enter__(self):
        self._session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self._session)

    def __exit__(self, *args):
        super().__exit__(*args)
        self._session.close()

    def rollback(self):
        self._session.rollback()
