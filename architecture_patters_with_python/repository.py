from sqlalchemy.orm import Session
import model


class Repository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, thing):
        self._session.add(thing)

    def get(self, reference) -> model.Batch:
        return (
            self._session.query(model.Batch)
            .filter_by(reference=reference)
            .one()
        )
