"""
Contains all application routes
"""

from flask import current_app as app


@app.route("/allocate", methods=["POST"])
def allocate():
    return {}, 200
