from __future__ import annotations
from datetime import date
from typing import Optional

from allocation.adapters import repository

from allocation.domain import model


class InvalidSku(Exception):
    def __init__(self, sku: str):
        self._message = f"Invalid sku {sku}"

    @property
    def message(self):
        return self._message


def allocate(
    orderid: str, sku: str, qty: str, repo: repository.AbstractRepository, session
):
    batches = repo.list()
    orderline = model.OrderLine(orderid=orderid, sku=sku, qty=qty)
    if orderline.sku not in {batch.sku for batch in batches}:
        raise InvalidSku(orderline.sku)
    batchref = model.allocate(orderline, batches)
    session.commit()
    return batchref


def add_batch(
    reference: str,
    sku: str,
    qty: str,
    eta: Optional[date],
    repo: repository.AbstractRepository,
    session,
):
    batch = model.Batch(reference=reference, sku=sku, qty=qty, eta=eta)
    repo.add(batch)
    session.commit()
    return batch.reference
