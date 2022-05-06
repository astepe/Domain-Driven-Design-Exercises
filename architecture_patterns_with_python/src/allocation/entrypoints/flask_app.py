from allocation import config
from allocation.adapters import orm
from allocation.adapters.repository import BatchRepository
from allocation.service_layer import services
from allocation.domain import model
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate():
    session = get_session()
    repo = BatchRepository(session)

    orderline = model.OrderLine(**request.json)
    batchref = services.allocate(orderline, repo, session)

    session.commit()
    return {"batchref": batchref}, 201


@app.errorhandler(model.OutOfStock)
def out_of_stock_handler(error):
    return {"error": error.message}, 400


@app.errorhandler(services.InvalidSku)
def out_of_stock_handler(error):
    return {"error": error.message}, 400
