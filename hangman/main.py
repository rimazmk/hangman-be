from . import app, redis_client
from flask import abort, request
import json


@app.route("/")
def get_state():
    roomID = request.args.get("roomID", default="", type=str)
    if roomID and redis_client.exists(roomID):
        return json.loads(redis_client.get(roomID))
    elif roomID and len(roomID) == 10:
        return abort(404)
    else:
        return abort(400)
