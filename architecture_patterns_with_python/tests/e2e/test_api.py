import random
import string
from uuid import uuid4
from allocation.domain import model

import pytest
import requests
from allocation import config


def random_batchref():
    return str(uuid4())


def random_sku():
    return "".join(random.sample(string.ascii_uppercase, k=5))


def random_id():
    return str(uuid4())


def add_batch(batch: dict):
    url = config.get_api_url()
    response = requests.post(
        f"{url}/add_batch",
        json=batch,
    )
    assert response.status_code == 201


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation():
    sku1, sku2 = random_sku(), random_sku()
    earlybatch = random_batchref()
    laterbatch = random_batchref()
    otherbatch = random_batchref()
    url = config.get_api_url()
    add_batch(
        {"reference": laterbatch, "sku": sku1, "qty": 100, "eta": "2020-06-03"},
    )
    add_batch(
        {"reference": earlybatch, "sku": sku1, "qty": 100, "eta": "2020-06-02"},
    )
    add_batch(
        {"reference": otherbatch, "sku": sku2, "qty": 100, "eta": None},
    )
    request_data = {"orderid": random_id(), "sku": sku1, "qty": 50}
    response = requests.post(f"{url}/allocate", json=request_data)
    assert response.status_code == 201
    assert response.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("restart_api")
def test_api_persists_batches():
    sku = random_sku()
    earlybatch = random_batchref()
    laterbatch = random_batchref()
    url = config.get_api_url()

    add_batch(
        {"reference": laterbatch, "sku": sku, "qty": 10, "eta": "2020-06-03"},
    )
    add_batch(
        {"reference": earlybatch, "sku": sku, "qty": 10, "eta": "2020-06-02"},
    )

    orderline1 = {"orderid": random_id(), "sku": sku, "qty": 10}
    orderline2 = {"orderid": random_id(), "sku": sku, "qty": 10}

    response = requests.post(f"{url}/allocate", json=orderline1)
    assert response.status_code == 201
    assert response.json()["batchref"] == earlybatch

    response = requests.post(f"{url}/allocate", json=orderline2)
    assert response.status_code == 201
    assert response.json()["batchref"] == laterbatch


@pytest.mark.usefixtures("restart_api")
def test_400_message_for_out_of_stock():
    sku = random_sku()
    laterbatch = random_batchref()

    add_batch(
        {"reference": laterbatch, "sku": sku, "qty": 10, "eta": "2020-06-03"},
    )
    orderline = {"orderid": random_id(), "sku": sku, "qty": 11}

    url = config.get_api_url()

    response = requests.post(f"{url}/allocate", json=orderline)
    assert response.status_code == 400
    assert response.json()["error"] == model.OutOfStock(sku=sku).message


@pytest.mark.usefixtures("restart_api")
def test_400_message_for_invalid_sku():
    unknown_sku = random_sku()
    orderline = {"orderid": random_id(), "sku": unknown_sku, "qty": 10}
    url = config.get_api_url()
    response = requests.post(f"{url}/allocate", json=orderline)
    assert response.status_code == 400
    assert response.json()["error"] == f"Invalid sku {unknown_sku}"
