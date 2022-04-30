from typing import Optional
from dataclasses import dataclass, field
from datetime import date


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


@dataclass
class Batch:
    reference: str
    sku: str
    qty: int
    eta: Optional[date] = None
    _allocations: set = field(init=False, default_factory=set)

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def allocate(self, orderline: OrderLine):
        if self.can_allocate(orderline):
            self._allocations.add(orderline)

    def can_allocate(self, orderline: OrderLine):
        return (
            self.available_quantity - orderline.qty >= 0
            and self.sku == orderline.sku
            and orderline not in self._allocations
        )

    def deallocate(self, orderline: OrderLine):
        if self.can_deallocate(orderline):
            self._allocations.remove(orderline)

    def can_deallocate(self, orderline: OrderLine):
        return orderline in self._allocations

    @property
    def allocated_qty(self) -> int:
        return sum(orderline.qty for orderline in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self.qty - self.allocated_qty


class OutOfStock(Exception):
    pass
