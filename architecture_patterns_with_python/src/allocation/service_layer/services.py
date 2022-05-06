from __future__ import annotations

from allocation.adapters import repository

from allocation.domain import model


class InvalidSku(Exception):
    def __init__(self, sku: str):
        self._message = f"Invalid sku {sku}"

    @property
    def message(self):
        return self._message


def allocate(orderline: model.OrderLine, repo: repository.BatchRepository, session):
    batches = repo.list()
    if orderline.sku not in {batch.sku for batch in batches}:
        raise InvalidSku(orderline.sku)
    batchref = model.allocate(orderline, batches)
    session.commit()
    return batchref
