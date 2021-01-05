from .db import *
from .game import *
from . import socketio
from flask_socketio import emit, close_room, leave_room, join_room
import random
import string


@socketio.on('chat')
def handle_message(info):
    res = [info['user'], info['message']]
    emit('chat', res, room=info['roomID'], include_self=False)


@socketio.on("create")
def create_game_handler(payload):
    while True:
        roomID = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10))

        if not exists(roomID):
            break

    join_room(roomID)
    print(f"{payload['username']} has entered the room: {roomID}")
    def_game_state = create_game(payload)
    set(roomID, def_game_state)
    emit('link', {'gameState': def_game_state, 'roomID': roomID})


@socketio.on('newRound')
def new_round_handler(payload):
    word, roomID, category, user = payload['word'], payload['roomID'], payload[
        'category'], payload['user']
    game_state = get(roomID)
    handle_new_round(game_state, category, word, user)
    set(roomID, game_state)
    emit('response', game_state, room=roomID)


@socketio.on('joinRoom')
def handle_join_room(roomID):
    join_room(roomID)


@socketio.on('join')
def handle_join(credentials):
    user, roomID = credentials['user'], credentials['roomID']
    game_state = get(roomID)
    add_player(game_state, user)
    join_room(roomID)
    set(roomID, game_state)
    print(f"{user} has entered the room: {roomID}")
    emit('update', game_state, room=roomID)


@socketio.on('start')
def handle_start(roomID):
    game_state = get(roomID)
    start_game(game_state)
    set(roomID, game_state)
    emit('update', game_state, room=roomID)


@socketio.on('guess')
def handle_guess(payload):
    game_state = payload['gameState']
    guess(game_state)
    set(payload['roomID'], game_state)
    emit('update', game_state, room=payload['roomID'])


@socketio.on('leave')
def on_leave(payload):
    username, roomID = payload['user'], payload['roomID']
    print(f"{username} left {roomID}")

    if roomID and exists(roomID):
        game_state = get(roomID)

        if num_players(game_state) == 1:
            close_room(roomID)
            delete(roomID)
        else:
            handle_leave(game_state, username)
            leave_room(roomID)
            set(roomID, game_state)
            emit('leave', game_state, room=roomID)


count = 0


@socketio.on('connect')
def handle_connect():
    global count
    count += 1
    print(count, " connected")


@socketio.on('disconnect')
def handle_disconnect():
    global count
    count -= 1
    print(count, " connected")
