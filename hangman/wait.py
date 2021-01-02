from . import socketio, redis_client
from flask_socketio import emit, join_room
import json


@socketio.on('joinRoom')
def handle_join_room(roomID):
    join_room(roomID)


@socketio.on('join')
def handle_join(credentials):
    username = credentials['user']
    roomID = credentials['roomID']
    game_state = json.loads(redis_client.get(roomID))

    game_state['players'].append(username)
    redis_client.set(roomID, json.dumps(game_state))
    join_room(roomID)
    print(f"{username} has entered the room: {roomID}")
    emit('update', game_state, room=roomID)


@socketio.on('start')
def handle_start(roomID):
    game_state = json.loads(redis_client.get(roomID))
    game_state['gameStart'] = True
    game_state['guesser'] = game_state["players"][1]
    redis_client.set(roomID, json.dumps(game_state))
    emit('update', game_state, room=roomID)
