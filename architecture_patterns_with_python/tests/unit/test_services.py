import uuid

import pytest
from allocation.service_layer import services
from tests.fakes import FakeUnitOfWork


def test_returns_allocations():
    fake_unit_of_work = FakeUnitOfWork()
    batch_reference = services.add_batch(
        str(uuid.uuid4()), "Red-Shirt", 20, None, fake_unit_of_work
    )
    result = services.allocate(str(uuid.uuid4()), "Red-Shirt", 10, fake_unit_of_work)
    assert result == batch_reference


def test_error_for_invalid_sku():
    fake_unit_of_work = FakeUnitOfWork()
    services.add_batch(str(uuid.uuid4()), "somesku", 10, None, fake_unit_of_work)
    with pytest.raises(services.InvalidSku) as error:
        services.allocate("oid", "invalid", 1, fake_unit_of_work)
        assert error.message == "Invalid sku invalid"


# def test_commit(fake_unit_of_work):
#     services.add_batch(str(uuid.uuid4()), "Red-Shirt", 20, None, fake_unit_of_work)
#     services.allocate(str(uuid.uuid4()), "Red-Shirt", 10, fake_unit_of_work)
#     assert fake_session.committed
