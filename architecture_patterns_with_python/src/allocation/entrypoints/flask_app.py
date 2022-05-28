from allocation.adapters import orm
from allocation.service_layer import services, unit_of_work
from allocation.domain import model
from flask import Flask, request

orm.start_mappers()
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate():
    batchref = services.allocate(
        **request.json, unit_of_work=unit_of_work.SqlAlchemyUnitOfWork()
    )

    return {"batchref": batchref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    services.add_batch(
        **request.json, unit_of_work=unit_of_work.SqlAlchemyUnitOfWork()
    )

    return {}, 201


@app.errorhandler(model.OutOfStock)
def out_of_stock_handler(error):
    return {"error": error.message}, 400


@app.errorhandler(services.InvalidSku)
def out_of_stock_handler(error):
    return {"error": error.message}, 400
