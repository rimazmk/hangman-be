from . import socketio, redis_client
from flask_socketio import close_room, emit, leave_room
import json


@socketio.on('leave')
def on_leave(data):
    username = data['user']
    roomID = data['roomID']
    print(f"ROOMID: {roomID}")

    if roomID and redis_client.exists(roomID):
        game_state = json.loads(redis_client.get(roomID))
    else:
        return

    def remove():
        try:
            game_state['players'].remove(username)
            leave_room(roomID)
            print(f"{username} has left the room: {roomID}")
        except ValueError:
            print(f"{username} not found")

    if len(game_state['players']) == 1:
        close_room(roomID)
        redis_client.delete(roomID)
        return
    elif len(game_state['players']) == 2:
        remove()
        game_state['hanger'] = game_state['players'][0]
        game_state['gameStart'] = False
    elif username == game_state['hanger']:
        remove()
        game_state['hanger'] = game_state['players'][0]
        game_state['guesser'] = game_state['players'][1]
        game_state['word'] = game_state['category'] = ""
    elif username == game_state['guesser']:
        guess_pos = game_state['players'].index(game_state['guesser'])
        next_guesser = (guess_pos + 1) % len(game_state['players'])
        jump = (next_guesser + 1) % len(game_state['players'])
        guess_pos = next_guesser if game_state['hanger'] != game_state['players'][next_guesser] else jump
        game_state['guesser'] = game_state['players'][guess_pos]
        remove()
    else:
        remove()

    redis_client.set(roomID, json.dumps(game_state))
    emit('leave', game_state, room=roomID)
