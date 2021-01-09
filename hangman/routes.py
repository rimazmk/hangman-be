"""Validate Rooms."""

from flask import abort, request, send_from_directory
from . import app
from .db import exists, get


@app.route("/")
def get_state():
    """
    Return a GameState object given a valid roomID.
    Otherwise, return a 404 error if room ID is invalid
    or a 400 error if request is malformed
    """
    roomID = request.args.get("roomID", default="", type=str)
    if roomID and exists(roomID):
        return get(roomID)
    if roomID and len(roomID) == 10:
        print("welp")
        return abort(404)
    return abort(400)

@app.route('/audio/<path:filename>')
def download_file(filename):
    print("here")
    return send_from_directory('../audio/', filename, as_attachment=True)
