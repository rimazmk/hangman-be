from flask import Flask, abort, request
from flask_socketio import SocketIO, close_room, emit, join_room, leave_room, rooms
from flask_redis import FlaskRedis
from flask_cors import CORS

import json
import string
import random

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = b''.join([
    b'\x92\xc6\xd6',
    b'\x1e;\x19_fl\xc0',
    b'\xf31\xc1N\xc0kT',
    b'\xb0s\x7f\xa1',
    b'\x8f\x03',
])

app.config['REDIS_URL'] = "redis://:@localhost:6379/0"

socketio = SocketIO(app, cors_allowed_origins='*')
redis_client = FlaskRedis(app, decode_responses=True)

print(socketio)

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
    # print(request.sid, type(request.sid), rooms())
    room = None
    for r in rooms():
        if r != request.sid:
            room = r
            break

    on_leave({'user': redis_client.get(request.sid), 'roomID': room, 'sid': request.sid})
    redis_client.delete(request.sid)
    print(count, " connected")


@socketio.on('leave')
def on_leave(data):
    username = data['user']
    roomID = data['roomID']
    print(f"ROOMID: {roomID}")
    game_state = json.loads(redis_client.get(roomID))

    def remove():
        try:
            game_state['players'].remove(username)
            leave_room(roomID, data['sid'])
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
    elif username == game_state['guesser']:
        guess_pos = game_state['players'].index(game_state['guesser'])
        next = (guess_pos + 1) % len(game_state['players'])
        jump = (next + 1) % len(game_state['players'])
        guess_pos = next if game_state['hanger'] != game_state['players'][next] else jump
        game_state['guesser'] = game_state['players'][guess_pos]
        remove()
    else:
        remove()

    redis_client.set(roomID, json.dumps(game_state))
    emit('leave', game_state, room=roomID)


@socketio.on('joinRoom')
def handle_join_room(roomID):
    join_room(roomID)


@socketio.on('newRound')
def handle_new_round(info):
    word, roomID = info['word'], info['roomID']
    game_state = json.loads(redis_client.get(roomID))
    game_state['word'] = word
    game_state['category'] = info['category']
    game_state['guessedWord'] = ''.join(
        ['#' if c.isalnum() else c for c in word])
    redis_client.set(roomID, json.dumps(game_state))
    emit('response', game_state, room=roomID)


@socketio.on('guess')
def handle_guess(msg):
    game_state = msg['gameState']
    cur = game_state['curGuess']

    if len(cur) == 1 and cur.isalpha():
        game_state['guessedLetters'].append(cur.lower())
        match = 0

        for i, (w, g) in enumerate(zip(game_state['word'], game_state['guessedWord'])):
            if w.lower() == cur.lower() and g == '#':
                game_state['guessedWord'] = game_state['guessedWord'][:i] + \
                    cur + game_state['guessedWord'][i + 1:]
                match += 1

        if match == 0:
            game_state['numIncorrect'] += 1

    else:
        game_state['guessedWords'].append(cur)

        if cur.lower() != game_state['word'].lower():
            game_state['numIncorrect'] += 1

    # TODO: Update wins variable here
    if (cur.lower() == game_state['word'].lower() or
        game_state['numIncorrect'] == game_state['lives'] or
            game_state['word'].lower() == game_state['guessedWord'].lower()):

        if game_state["numIncorrect"] != game_state['lives']:
            game_state["hanger"] = msg['user']

        hang_pos = game_state['players'].index(game_state['hanger'])
        guess_pos = hang_pos + \
            1 if hang_pos != (len(game_state['players']) - 1) else 0
        game_state['guesser'] = game_state['players'][guess_pos]

        # TODO: Transition to newRound without relying on category
        # game_state['word'] = ""
        game_state['category'] = game_state['curGuess'] = game_state['guessedWord'] = ""
        game_state['guessedLetters'], game_state['guessedWords'] = [], []
        game_state['numIncorrect'] = 0
    else:
        guess_pos = game_state['players'].index(game_state['guesser'])
        guess_pos = (guess_pos + 1) % len(game_state['players'])
        hang_pos = game_state['players'].index(game_state['hanger'])

        if guess_pos == hang_pos:
            guess_pos = (guess_pos + 1) % len(game_state['players'])
        game_state['guesser'] = game_state['players'][guess_pos]

    redis_client.set(msg['roomID'], json.dumps(game_state))
    emit('guess', game_state, room=msg['roomID'])


@socketio.on('join')
def handle_join(credentials):
    username = credentials['user']
    roomID = credentials['roomID']
    game_state = json.loads(redis_client.get(roomID))
    redis_client.set(request.sid, username)

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


@app.route("/")
def get_state():
    roomID = request.args.get("roomID", default="", type=str)
    if roomID and redis_client.exists(roomID):
        return json.loads(redis_client.get(roomID))
    elif roomID and len(roomID) == 10:
        return abort(404)
    else:
        return abort(400)


@socketio.on("create")
def create_game(params):
    while True:
        roomID = ''.join(random.choices(string.ascii_uppercase +
                                        string.digits, k=10))
        if not redis_client.exists(roomID):
            break

    guessed_word = ''.join(
        ['#' if c.isalnum() else c for c in params['word']])

    # TODO: Get word and category input at game screen
    def_game_state = {'players': [params['username']],
                      'hanger': params['username'],
                      'category': params['category'],
                      'word': params['word'],
                      'guessedLetters': [],
                      'numIncorrect': 0,
                      'lives': int(params['lives']),
                      'guessedWords': [],
                      'guesser': None,
                      'curGuess': None,
                      'guessedWord': guessed_word,
                      'gameStart': False,
                      'cap': 8
                      }

    redis_client.set(request.sid, params['username'])
    join_room(roomID)
    print(f"{params['username']} has entered the room: {roomID}")

    redis_client.set(roomID, json.dumps(def_game_state))
    response = {'gameState': def_game_state, 'roomID': roomID}
    emit('link', response)


if __name__ == '__main__':
    socketio.run(app)
