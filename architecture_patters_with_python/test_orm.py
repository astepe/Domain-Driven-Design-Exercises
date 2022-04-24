import model

def test_orderline_mapper_can_load_lines(session):
    session.execute(
        "INSERT INTO orderlines (sku, qty, orderid) VALUES"
        " ('RED-CHAIR', 12, 'order1'),"
        " ('RED-TABLE', 13, 'order1'),"
        " ('BLUE-LIPSTICK', 14, 'order2')"
    )
    expected = [
        model.OrderLine(sku="RED-CHAIR", qty=12, orderid="order1"),
        model.OrderLine(sku="RED-TABLE", qty=13, orderid="order1"),
        model.OrderLine(sku="BLUE-LIPSTICK", qty=14, orderid="order2"),
    ]
    assert session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    orderline = model.OrderLine(sku="RED-CHAIR", qty=12, orderid="order1")
    session.add(orderline)
    session.commit()

    rows = list(session.execute("SELECT orderid, sku, qty FROM orderlines"))

    assert rows == [("order1", "RED-CHAIR", 12)]
