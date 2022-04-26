from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Date,
)
from sqlalchemy.orm import mapper, relationship

import model

metadata = MetaData()

orderlines = Table(
    "orderlines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("batch_id", ForeignKey("batches.id")),
    Column("orderline_id", ForeignKey("orderlines.id")),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("qty", Integer),
    Column("eta", Date, nullable=True),
)


def start_mappers():
    orderline_mapper = mapper(model.OrderLine, orderlines)
    batch_mapper = mapper(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                orderline_mapper, secondary=allocations, collection_class=set
            )
        },
    )
