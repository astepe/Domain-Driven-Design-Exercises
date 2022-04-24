from datetime import date
from uuid import uuid4
import model
from repository import Repository


def test_repository_can_save_a_batch(session):
    batch_reference = str(uuid4())
    batch = model.Batch(batch_reference, "RED-SHIRT", 100)

    repository = Repository(session)
    repository.add(batch)
    session.commit()

    assert session.query(model.Batch).all() == [
        model.Batch(batch_reference, "RED-SHIRT", 100, None)
    ]


def test_repository_can_retrieve_a_batch_with_allocations(session):
    session.execute(
        'INSERT INTO orderlines (orderid, sku, qty)'
        ' VALUES ("order1", "RED-SHIRT", 5)'
    )

    [[orderline_id]] = session.execute(
        'SELECT id FROM orderlines WHERE orderid=:orderid AND sku=:sku',
        dict(orderid="order1", sku="RED-SHIRT")
    )
    
    session.execute(
        'INSERT INTO batches (reference, sku, qty, eta)'
        'VALUES ("batch1", "RED-SHIRT", 10, :eta)',
        dict(eta=date.today())
    )

    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:reference AND sku=:sku',
        dict(reference="batch1", sku="RED-SHIRT")
    )

    session.execute(
        'INSERT INTO allocations (batch_id, orderline_id)'
        'VALUES (:batch_id, :orderline_id)',
        dict(batch_id=batch_id, orderline_id=orderline_id)
    )

    repository = Repository(session)
    retrieved = repository.get("batch1")

    expected = model.Batch("batch1", "RED-SHIRT", 10, eta=date.today())
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved.qty == expected.qty
    assert retrieved.eta == expected.eta
    assert retrieved._allocations == {
        model.OrderLine("order1", "RED-SHIRT", 5)
    }
