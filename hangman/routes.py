"""Validate Rooms."""

from flask import abort, request, send_from_directory
from flask_mail import Message
from . import app, mail
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
        return abort(404)
    return abort(400)


@app.route('/audio/<path:filename>')
def get_file(filename):
    """Return audio file for game SFX."""
    return send_from_directory('../audio/', filename, as_attachment=True)


@app.route('/feedback/', methods=['POST'])
def send_mail():
    """Send feedback to site email."""
    info = request.get_json()['data']
    msg = Message(f"Feedback from {info['first']} {info['last']}", recipients=[
                  'hangmanonlinefeedback@gmail.com'])
    msg.body = f"{info['email']}\n\n{info['feedback']}"
    mail.send(msg)
    return "Sent"
