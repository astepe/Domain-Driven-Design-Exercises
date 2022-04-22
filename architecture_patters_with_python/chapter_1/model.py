from typing import Optional
import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    quantity: int


@dataclass
class Batch:
    reference: str
    sku: str
    available_quantity: int
    eta: Optional[date] = None
    allocated_orderlines: set = field(init=False, default_factory=set)

    def allocate(self, orderline: OrderLine):
        if self.can_allocate(orderline):
            self.available_quantity -= orderline.quantity
            self.allocated_orderlines.add(orderline)

    def can_allocate(self, orderline: OrderLine):
        return (
            self.available_quantity - orderline.quantity >= 0
            and self.sku == orderline.sku
            and orderline not in self.allocated_orderlines
        )
    
    def can_deallocate(self, orderline: OrderLine):
        return orderline in self.allocated_orderlines
    
    def deallocate(self, orderline: OrderLine):
        if self.can_deallocate(orderline):
            self.available_quantity += orderline.quantity
            self.allocated_orderlines.remove(orderline)
