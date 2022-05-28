from __future__ import annotations
from datetime import date
from typing import Optional

from allocation.adapters import repository

from allocation.domain import model
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    def __init__(self, sku: str):
        self._message = f"Invalid sku {sku}"

    @property
    def message(self):
        return self._message


def allocate(
    orderid: str, sku: str, qty: str, unit_of_work: unit_of_work.AbstractUnitOfWork,
):
    with unit_of_work:
        batches = unit_of_work.batches.list()
        orderline = model.OrderLine(orderid=orderid, sku=sku, qty=qty)
        if orderline.sku not in {batch.sku for batch in batches}:
            raise InvalidSku(orderline.sku)
        batchref = model.allocate(orderline, batches)
        unit_of_work.commit()

    return batchref


def add_batch(
    reference: str,
    sku: str,
    qty: str,
    eta: Optional[date],
    unit_of_work: unit_of_work.AbstractUnitOfWork,
):
    with unit_of_work:
        batch = model.Batch(reference=reference, sku=sku, qty=qty, eta=eta)
        unit_of_work.batches.add(batch)
        unit_of_work.commit()
