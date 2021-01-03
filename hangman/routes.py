from . import app
from .db import exists, get
from flask import abort, request


@app.route("/")
def get_state():
    roomID = request.args.get("roomID", default="", type=str)
    if roomID and exists(roomID):
        return get(roomID)
    elif roomID and len(roomID) == 10:
        return abort(404)
    else:
        return abort(400)
