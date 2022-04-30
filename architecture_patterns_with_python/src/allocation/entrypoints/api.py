"""
Contains all application routes
"""

from flask import current_app as app
from flask import g, jsonify, request
from sqlalchemy import asc


@app.route("/allocate", methods=["POST"])
def allocate():
    return {}, 200
