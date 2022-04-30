from __future__ import annotations
from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.domain.model import OrderLine
from allocation.adapters.repository import AbstractRepository


def allocate(orderline: OrderLine, batches: list[model.Batch]):
    try:
        earliest_batch = next(
            batch
            for batch in sorted(
                batches,
                key=lambda batch: batch.eta if batch.eta is not None else date.today(),
            )
            if batch.can_allocate(orderline)
        )
        earliest_batch.allocate(orderline)
        return earliest_batch.reference
    except StopIteration as error:
        raise model.OutOfStock from error