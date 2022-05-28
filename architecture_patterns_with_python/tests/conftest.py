import time
from pathlib import Path

import pytest
import requests
from allocation import config
from allocation.adapters import orm, repository
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import clear_mappers, sessionmaker

from allocation.domain import model


class FakeRepository(repository.BatchRepository):
    def __init__(self, batches: list[model.Batch]):
        self._batches = {batch.reference: batch for batch in batches}

    def add(self, batch: model.Batch):
        self._batches[batch.reference] = batch

    def get(self, reference) -> model.Batch:
        return self._batches.get(reference, None)

    def list(self) -> list[model.Batch]:
        return list(self._batches.values())


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


@pytest.fixture(name="fake_repository")
def fake_repository_fixture():
    return FakeRepository([])


@pytest.fixture(name="fake_session")
def fake_session_fixture():
    return FakeSession()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    uri = config.get_postgres_uri()
    while time.time() < deadline:
        try:
            return engine.connect(uri)
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


@pytest.fixture(name="in_memory_session")
def in_memory_session_fixture(in_memory_engine):
    orm.start_mappers()
    yield sessionmaker(bind=in_memory_engine)()
    clear_mappers()


@pytest.fixture(name="in_memory_engine")
def in_memory_engine_fixture():
    engine = create_engine("sqlite:///:memory:")
    orm.metadata.create_all(engine)
    return engine


@pytest.fixture(name="postgres_session")
def postgres_session_fixture(postgres_engine):
    orm.start_mappers()
    yield sessionmaker(bind=postgres_engine)()
    clear_mappers()


@pytest.fixture(name="postgres_engine")
def postgres_engine_fixture():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    orm.metadata.create_all(engine)
    return engine


@pytest.fixture(name="add_stock")
def add_stock_fixture():

    batches_added = set()
    skus_added = set()
    db_session = None
    def add_stock(session, batches):
        nonlocal db_session
        db_session = session
        for reference, sku, qty, eta in batches:
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
        db_session.execute(
            'DELETE FROM allocations WHERE batch_id=:batch_id',
            dict(batch_id=batch_id)
        )
        db_session.execute(
            'DELETE FROM batches WHERE id=:batch_id',
            dict(batch_id=batch_id)
        )
    for sku in skus_added:
        db_session.execute(
            'DELETE FROM orderlines WHERE sku=:sku',
            dict(sku=sku)
        )
    db_session.commit()


@pytest.fixture(name="restart_api")
def restart_api_fixture():
    (Path(__file__).parent / "../src/allocation/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
