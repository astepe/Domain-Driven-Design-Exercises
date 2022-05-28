import uuid

from allocation.service_layer import services
import pytest


def test_returns_allocations(fake_repository, fake_session):
    batch_reference = services.add_batch(
        str(uuid.uuid4()), "Red-Shirt", 20, None, fake_repository, fake_session
    )
    result = services.allocate(str(uuid.uuid4()), "Red-Shirt", 10, fake_repository, fake_session)
    assert result == batch_reference


def test_error_for_invalid_sku(fake_repository, fake_session):
    services.add_batch(str(uuid.uuid4()), "somesku", 10, None, fake_repository, fake_session)
    with pytest.raises(services.InvalidSku) as error:
        services.allocate("oid", "invalid", 1, fake_repository, fake_session)
        assert error.message == "Invalid sku invalid"


def test_commit(fake_repository, fake_session):
    services.add_batch(str(uuid.uuid4()), "Red-Shirt", 20, None, fake_repository, fake_session)
    services.allocate(str(uuid.uuid4()), "Red-Shirt", 10, fake_repository, fake_session)
    assert fake_session.committed
