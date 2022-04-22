from chapter_1.service import allocate
from datetime import date, timedelta
import uuid
from chapter_1.model import Batch, OrderLine


def create_orderline_and_batch(sku, line_quantity, batch_quantity):
    return OrderLine(str(uuid.uuid4()), sku, line_quantity), Batch(
        "instock", sku, batch_quantity
    )


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


def test_cannot_allocate_orderline_if_skus_no_not_match():
    orderline, batch = OrderLine(str(uuid.uuid4()), "sku1", 2), Batch(
        "instock", "sku2", 3
    )
    assert batch.can_allocate(orderline) is False


def test_orderline_deallocation_increases_batch_up_to_original_qty():
    orderline, batch = OrderLine(str(uuid.uuid4()), "sku1", 2), Batch(
        "instock", "sku1", 6
    )
    batch.allocate(orderline)
    batch.deallocate(orderline)
    assert batch.available_quantity == 6


def test_orderline_allocation_is_idempotent():
    orderline, batch = OrderLine(str(uuid.uuid4()), "sku1", 2), Batch(
        "instock", "sku1", 6
    )
    batch.allocate(orderline)
    batch.allocate(orderline)
    assert batch.available_quantity == 4


def test_prefer_in_stock_batch_to_shipment_batch():
    in_stock_batch = Batch("instock", "T-Shirt", 100, eta=None)
    shipment_batch = Batch("shipment", "T-Shirt", 100, eta=date.today() + timedelta(days=1))

    orderline = OrderLine(str(uuid.uuid4()), "T-Shirt", 10)

    allocate(orderline, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefer_earlier_batches():
    early_batch = Batch("early", "T-Shirt", 100, eta=date.today())
    medium_batch = Batch("early", "T-Shirt", 100, eta=date.today() + timedelta(days=1))
    late_batch = Batch("early", "T-Shirt", 100, eta=date.today() + timedelta(days=2))

    orderline = OrderLine(str(uuid.uuid4()), "T-Shirt", 10)

    allocate(orderline, [medium_batch, late_batch, early_batch])

    assert early_batch.available_quantity == 90
    assert medium_batch.available_quantity == 100
    assert late_batch.available_quantity == 100