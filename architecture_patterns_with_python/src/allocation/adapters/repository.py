import abc
from allocation.domain import model
from sqlalchemy.orm import Session


class AbstractRepository(abc.ABC):
    
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        pass
    
    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        pass


class SqlAlchemyRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, thing):
        self._session.add(thing)

    def get(self, reference) -> model.Batch:
        return self._session.query(model.Batch).filter_by(reference=reference).one()

    def get_by_sku(self, sku) -> model.Batch:
        return self._session.query(model.Batch).filter_by(sku=sku).all()
    
    def list(self) -> list[model.Batch]:
        return self._session.query(model.Batch).all()
