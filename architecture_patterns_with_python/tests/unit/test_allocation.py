import uuid
from datetime import date, timedelta

import pytest
from allocation.domain import model


def create_orderline_and_batch(
    sku: str, line_quantity: int, batch_quantity: int
) -> tuple[model.OrderLine, model.Batch]:
    return model.OrderLine(str(uuid.uuid4()), sku, line_quantity), model.Batch(
        "instock", sku, batch_quantity
    )


def test_orderline_deallocation_increases_batch_available_quantity():
    orderline, batch = create_orderline_and_batch("T-Shirt", 3, 5)
    batch.allocate(orderline)
    assert batch.available_quantity == 2
    batch.deallocate(orderline)
    assert batch.available_quantity == 5


def test_orderline_allocation_reduces_batch_available_quantity():
    orderline, batch = create_orderline_and_batch("T-Shirt", 3, 5)
    batch.allocate(orderline)
    assert batch.available_quantity == 2


def test_can_allocate_orderline_if_available_quantity_equal_to_orderline_quantity():
    orderline, batch = create_orderline_and_batch("T-Shirt", 5, 5)
    assert batch.can_allocate(orderline)


def test_cannot_allocate_orderline_if_available_quantity_less_than_orderline_quantity():
    orderline, batch = create_orderline_and_batch("T-Shirt", 6, 5)
    assert batch.can_allocate(orderline) is False


def test_cannot_allocate_orderline_if_skus_dont_match():
    orderline, batch = model.OrderLine(str(uuid.uuid4()), "sku1", 2), model.Batch(
        "instock", "sku2", 3
    )
    assert batch.can_allocate(orderline) is False


def test_orderline_allocation_is_idempotent():
    orderline, batch = model.OrderLine(str(uuid.uuid4()), "sku1", 2), model.Batch(
        "instock", "sku1", 6
    )
    batch.allocate(orderline)
    batch.allocate(orderline)
    assert batch.available_quantity == 4


def test_prefer_in_stock_batch_to_shipment_batch():
    in_stock_batch = model.Batch("instock", "T-Shirt", 100, eta=None)
    shipment_batch = model.Batch(
        "shipment", "T-Shirt", 100, eta=date.today() + timedelta(days=1)
    )

    orderline = model.OrderLine(str(uuid.uuid4()), "T-Shirt", 10)

    model.allocate(orderline, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefer_earlier_batches():
    early_batch = model.Batch("early", "T-Shirt", 100, eta=date.today())
    medium_batch = model.Batch(
        "early", "T-Shirt", 100, eta=date.today() + timedelta(days=1)
    )
    late_batch = model.Batch(
        "early", "T-Shirt", 100, eta=date.today() + timedelta(days=2)
    )

    orderline = model.OrderLine(str(uuid.uuid4()), "T-Shirt", 10)

    model.allocate(orderline, [medium_batch, late_batch, early_batch])

    assert early_batch.available_quantity == 90
    assert medium_batch.available_quantity == 100
    assert late_batch.available_quantity == 100


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = model.Batch("today", "T-Shirt", 10, eta=date.today())
    model.allocate(model.OrderLine(str(uuid.uuid4()), "T-Shirt", 10), [batch])

    with pytest.raises(model.OutOfStock):
        model.allocate(model.OrderLine(str(uuid.uuid4()), "T-Shirt", 1), [batch])
