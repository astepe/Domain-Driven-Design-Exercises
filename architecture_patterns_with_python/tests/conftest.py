from uuid import uuid4
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import orm


@pytest.fixture(name="session")
def session_fixture(engine):
    orm.start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine("sqlite:///:memory:")
    orm.metadata.create_all(engine)
    return engine


@pytest.fixture(name="add_stock")
def add_stock_fixture(session):

    batches_added = set()
    skus_added = set()
    def add_stock(orderlines):

        for reference, sku, qty, eta in orderlines:
            session.execute(
                'INSERT INTO batches (reference, sku, qty, eta)'
                ' VALUES (:reference, :sku, :qty, :eta)',
                dict(reference=reference, sku=sku, qty=qty, eta=eta)
            )
            [[batch_id]] = session.execute(
                'SELECT id FROM batches WHERE reference=:reference AND sku=:sku',
                dict(reference=reference, sku=sku)
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        session.commit()
    
    yield add_stock

    for batch_id in batches_added:
        session.execute(
            'DELETE FROM batches WHERE id=:batch_id',
            dict(batch_id=batch_id)
        )
        session.execute(
            'DELETE FROM allocations WHERE batch_id=:batch_id',
            dict(batch_id=batch_id)
        )
    for sku in skus_added:
        session.execute(
            'DELETE FROM orderlines WHERE sku=:sku',
            
        )
