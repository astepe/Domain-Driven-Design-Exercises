import uuid
from allocation.adapters import repository
from allocation.domain import model
from allocation.service_layer import services
import pytest

from tests.unit.test_allocation import (
    create_orderline_and_batch,
)


class FakeRepository(repository.BatchRepository):
    def __init__(self, batches: list[model.Batch]):
        self._batches = {batch.reference: batch for batch in batches}

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference) -> model.Batch:
        return self._batches.get(reference, None)

    def list(self) -> list[model.Batch]:
        return list(self._batches.values())


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocations():
    orderline, batch = create_orderline_and_batch("Red-Shirt", 10, 50)
    repo = FakeRepository([batch])
    result = services.allocate(orderline, repo, FakeSession())
    assert result == batch.reference


def test_error_for_invalid_sku():
    orderline = model.OrderLine("oid", "invalid", 1)
    batch = model.Batch("bref", "somesku", 10)
    repo = FakeRepository([batch])
    with pytest.raises(services.InvalidSku) as error:
        services.allocate(orderline, repo, FakeSession())
        assert error.message == "Invalid sku invalid"


def test_commit():
    orderline, batch = create_orderline_and_batch("Red-Shirt", 10, 50)
    repo = FakeRepository([batch])
    session = FakeSession()
    services.allocate(orderline, repo, session)
    assert session.committed
