from allocation.adapters import repository
from allocation.domain import model
from allocation.service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository(repository.SqlAlchemyRepository):
    def __init__(self, batches: list[model.Batch]):
        self._batches = {batch.reference: batch for batch in batches}

    def add(self, batch: model.Batch):
        self._batches[batch.reference] = batch

    def get(self, reference) -> model.Batch:
        return self._batches.get(reference, None)

    def list(self) -> list[model.Batch]:
        return list(self._batches.values())


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def rollback(self):
        pass
