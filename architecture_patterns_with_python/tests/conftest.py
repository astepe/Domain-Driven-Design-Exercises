import time
from pathlib import Path

import pytest
import requests
from allocation import config
from allocation.adapters import orm
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import clear_mappers, sessionmaker


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


@pytest.fixture(name="session_factory")
def session_factory_fixture(in_memory_engine):
    orm.start_mappers()
    yield sessionmaker(bind=in_memory_engine)
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


@pytest.fixture(name="restart_api")
def restart_api_fixture():
    (Path(__file__).parent / "../src/allocation/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
