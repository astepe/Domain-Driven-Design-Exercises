from chapter_1.model import Batch, OrderLine
from datetime import date


def allocate(orderline: OrderLine, batches: list[Batch]):
    earliest_batch = next(
        batch
        for batch in sorted(
            batches,
            key=lambda batch: batch.eta if batch.eta is not None else date.today(),
        )
        if batch.can_allocate(orderline)
    )
    earliest_batch.allocate(orderline)
