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


def random_orderid():
    return str(uuid4())


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock, postgres_session):
    sku1, sku2 = random_sku(), random_sku()
    earlybatch = random_batchref()
    laterbatch = random_batchref()
    otherbatch = random_batchref()

    add_stock(postgres_session, [
        (laterbatch, sku1, 100, '2020-06-03'),
        (earlybatch, sku1, 100, '2020-06-02'),
        (otherbatch, sku2, 100, None),
    ])
    request_data = {'orderid': random_orderid(), 'sku': sku1, 'qty': 50}
    url = config.get_api_url()
    response = requests.post(f'{url}/allocate', json=request_data)
    assert response.status_code == 201
    assert response.json()['batchref'] == earlybatch


@pytest.mark.usefixtures("restart_api")
def test_api_persists_batches(add_stock, postgres_session):
    sku = random_sku()
    earlybatch = random_batchref()
    laterbatch = random_batchref()

    add_stock(postgres_session, [
        (laterbatch, sku, 10, '2020-06-03'),
        (earlybatch, sku, 10, '2020-06-02'),
    ])
    orderline1 = {'orderid': random_orderid(), 'sku': sku, 'qty': 10}
    orderline2 = {'orderid': random_orderid(), 'sku': sku, 'qty': 10}

    url = config.get_api_url()

    response = requests.post(f'{url}/allocate', json=orderline1)
    assert response.status_code == 201
    assert response.json()['batchref'] == earlybatch

    response = requests.post(f'{url}/allocate', json=orderline2)
    assert response.status_code == 201
    assert response.json()['batchref'] == laterbatch


@pytest.mark.usefixtures("restart_api")
def test_400_message_for_out_of_stock(add_stock, postgres_session):
    sku = random_sku()
    laterbatch = random_batchref()

    add_stock(postgres_session, [
        (laterbatch, sku, 10, '2020-06-03'),
    ])
    orderline = {'orderid': random_orderid(), 'sku': sku, 'qty': 11}

    url = config.get_api_url()

    response = requests.post(f'{url}/allocate', json=orderline)
    assert response.status_code == 400
    assert response.json()['error'] == model.OutOfStock(sku=sku).message


@pytest.mark.usefixtures("restart_api")
def test_400_message_for_invalid_sku():
    unknown_sku = random_sku()
    orderline = {'orderid': random_orderid(), 'sku': unknown_sku, 'qty': 10}
    url = config.get_api_url()
    response = requests.post(f'{url}/allocate', json=orderline)
    assert response.status_code == 400
    assert response.json()['error'] == f"Invalid sku {unknown_sku}"
