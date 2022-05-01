import random
import string
from uuid import uuid4
import pytest


def random_batchref():
    return str(uuid4())


def random_sku():
    return "".join(random.sample(string.ascii_uppercase, k=5))


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock):
    sku1, sku2 = random_sku(), random_sku()
    earlybatch = random_batchref()
    laterbatch = random_batchref()
    otherbatch = random_batchref()

    add_stock([
        (laterbatch, sku1, 100, '2020-06-03'),
        (earlybatch, sku1, 100, '2020-06-02'),
        (otherbatch, sku2, 100, None),
    ])
