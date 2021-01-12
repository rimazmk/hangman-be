"""Handle Incoming Socket Messages."""

from typing import Dict, Union
import random
import string
from flask_socketio import emit, close_room, leave_room, join_room
from .db import upsert, get, exists, delete
from .game import (create_game, start_game, add_player, num_players,
                   handle_leave, handle_new_round, guess)
from . import socketio, GameState


@socketio.on('chat')
def handle_message(info: Dict[str, str]):
    """Send new message to all players."""
    res = [info['user'], info['message']]
    include = info['user'] not in ["join", "leave"]
    emit('chat', res, room=info['roomID'], include_self=include)


@socketio.on("create")
def create_game_handler(payload: Dict[str, str]):
    """Create roomID and GameState object."""
    while True:
        roomID = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10))

        if not exists(roomID):
            break

    join_room(roomID)
    print(f"{payload['username']} has entered the room: {roomID}")
    def_game_state = create_game(payload)
    upsert(roomID, def_game_state)
    emit('link', {'gameState': def_game_state, 'roomID': roomID})


@socketio.on('newRound')
def new_round_handler(payload: Dict[str, str]):
    """Update GameState object with the parameters for the new round."""
    word, roomID, category, user = payload['word'], payload['roomID'], payload[
        'category'], payload['user']
    game_state = get(roomID)
    handle_new_round(game_state, category, word, user)
    upsert(roomID, game_state)
    emit('response', game_state, room=roomID)


@socketio.on('joinRoom')
def handle_join_room(roomID: str):
    """Add user to the room."""
    join_room(roomID)


@socketio.on('join')
def handle_join(credentials: Dict[str, str]):
    """Add user to the GameState and send updated GameState to all players."""
    user, roomID = credentials['user'], credentials['roomID']
    game_state = get(roomID)
    add_player(game_state, user)
    join_room(roomID)
    upsert(roomID, game_state)
    print(f"{user} has entered the room: {roomID}")
    emit('update', game_state, room=roomID)


@socketio.on('start')
def handle_start(roomID: str):
    """Start the game and send GameState to all players."""
    game_state = get(roomID)
    start_game(game_state)
    upsert(roomID, game_state)
    emit('update', game_state, room=roomID)


@socketio.on('guess')
def handle_guess(payload: Dict[str, Union[GameState, str]]):
    """Update GameState and send to all players."""
    game_state = payload['gameState']
    status = guess(game_state)
    # print(status)
    upsert(payload['roomID'], game_state)
    emit('status', status, room=payload['roomID'])
    emit('update', game_state, room=payload['roomID'])


@socketio.on('leave')
def on_leave(payload: Dict[str, str]):
    """Update the GameState and send to all remaining players."""
    username, roomID = payload['user'], payload['roomID']
    print(f"{username} left {roomID}")

    if username and roomID and exists(roomID):
        game_state = get(roomID)

        if num_players(game_state) == 1:
            game_state['players'] = []
            game_state['wins'] = {}
            emit('leave', game_state, room=roomID)
            close_room(roomID)
            delete(roomID)
        else:
            handle_leave(game_state, username)
            leave_room(roomID)
            upsert(roomID, game_state)
            emit('leave', game_state, room=roomID)
            handle_message({
                'user': 'leave',
                'message': f"{username} has left",
                'roomID': roomID
            })


count = 0


@socketio.on('connect')
def handle_connect():
    """Increment count of connected players."""
    global count
    count += 1
    print(count, " connected")


@socketio.on('disconnect')
def handle_disconnect():
    """Decrement count of connected players."""
    global count
    count -= 1
    print(count, " connected")
