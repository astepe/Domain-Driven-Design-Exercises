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
