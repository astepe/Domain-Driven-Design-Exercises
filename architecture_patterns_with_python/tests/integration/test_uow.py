from uuid import uuid4
import pytest

from requests import session

from allocation.domain import model
from allocation.service_layer import unit_of_work


def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        "INSERT INTO batches (reference, sku, qty, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batchref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        "SELECT id FROM orderlines WHERE orderid=:orderid and sku=:sku",
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(
        "SELECT b.reference FROM allocations JOIN batches as b ON batch_id = b.id"
        " WHERE orderline_id=:orderlineid",
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    input_batchref = str(uuid4())
    insert_batch(session, input_batchref, "Red-Shirt", 10, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get(reference=input_batchref)
        orderline = model.OrderLine("o1", "Red-Shirt", 10)
        batch.allocate(orderline)
        uow.commit()

    allocated_batchref = get_allocated_batchref(session, "o1", "Red-Shirt")
    assert allocated_batchref == input_batchref


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow._session, str(uuid4()), "Red-Shirt", 10, None)

    new_session = session_factory()
    assert list(new_session.execute("SELECT * FROM batches")) == []


def test_rolls_back_on_exception(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)

    class TestException(Exception):
        pass

    with pytest.raises(TestException):
        with uow:
            insert_batch(uow._session, str(uuid4()), "Red-Shirt", 10, None)
            raise TestException()

    new_session = session_factory()
    assert list(new_session.execute("SELECT * FROM batches")) == []
