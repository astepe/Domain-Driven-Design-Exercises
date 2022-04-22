from chapter_1.model import Batch, OrderLine
from datetime import date


class OutOfStock(Exception):
    pass


def allocate(orderline: OrderLine, batches: list[Batch]):
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
    except StopIteration as error:
        raise OutOfStock from error
