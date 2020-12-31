from flask import Flask, abort, request
from flask_socketio import SocketIO, send, emit
from flask_redis import FlaskRedis
from flask_cors import CORS

import json
import string
import random

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret!'
app.config['REDIS_URL'] = "redis://:@localhost:6379/0"

socketio = SocketIO(app, cors_allowed_origins='*')
print(socketio)
redis_client = FlaskRedis(app)

count = 0

@socketio.on('connect')
def connect():
    global count
    count += 1
    print(count, " connected")


@socketio.on('disconnect')
def disconnect():
    global count
    count -= 1
    print(count, " connected")

# @socketio.on('connect')
# def hello():
#     print("client connected")

@socketio.on('message')
def handle_message(message):
    # print('received message: ', message)
    emit('response', message)

@socketio.on('newRound')
def handle_newRound(info):
    # print('received message: ', message)
    category = info['category']
    word = info['word']
    roomID = info["roomID"]
    gameState = redis_client.get(roomID)
    gameState = json.loads(gameState)
    gameState['word'] = word
    gameState['category'] = category
    guessedWord = ['#' if c.isalnum() else c for c in word]
    gameState['guessedWord'] = ''.join(guessedWord)
    redis_client.set(roomID, json.dumps(gameState))
    emit('response', gameState, broadcast=True)

@socketio.on('guess')
def handle_guess(msg):
    gameState = msg['gameState']
    cur = gameState['curGuess']

    print(gameState, cur)
    print("received guess!")

    if len(cur) == 1:
        gameState['guessedLetters'].append(cur.lower())
        match = 0
        # Frontend prevents user from guessing a previously guessed letter
        for i, (w, g) in enumerate(zip(gameState['word'], gameState['guessedWord'])):
            if w.lower() == cur.lower() and g == '#':
                gameState['guessedWord'] = gameState['guessedWord'][:i] + cur + gameState['guessedWord'][i + 1:]
                match += 1

        if match == 0:
            gameState['numIncorrect'] += 1

    else:
        gameState['guessedWords'].append(cur)

        if cur.lower() != gameState['word'].lower():
            gameState['numIncorrect'] += 1

    # TODO: Update wins variable here
    if (cur.lower() == gameState['word'].lower()
        or gameState['numIncorrect'] == gameState['lives']
        or gameState['word'].lower() == gameState['guessedWord'].lower()):
        if gameState["numIncorrect"] == gameState['lives']:
            hangPos = gameState['players'].index(gameState['hanger'])
            guessPos = hangPos + 1 if hangPos != (len(gameState['players']) - 1) else 0
            gameState['guesser'] = gameState['players'][guessPos]
        else:
            gameState["hanger"] = msg['user']
            hangPos = gameState['players'].index(gameState['hanger'])
            guessPos = hangPos + 1 if hangPos != (len(gameState['players']) - 1) else 0
            gameState['guesser'] = gameState['players'][guessPos]

        # gameState['word'] = ""
        gameState['category'] = ""
        gameState['guessedLetters'] = []
        gameState['numIncorrect'] = 0
        gameState['guessedWords'] = []
        gameState['curGuess'] = ""
        gameState['guessedWord'] = ""
    else:
        guessPos = gameState['players'].index(gameState['guesser'])
        hangPos = gameState['players'].index(gameState['hanger'])
        guessPos = (guessPos + 1) % len(gameState['players'])
        if guessPos == hangPos:
            guessPos = (guessPos + 1) % len(gameState['players'])
        gameState['guesser'] = gameState['players'][guessPos]

    redis_client.set(msg['roomID'], json.dumps(gameState))
    emit('guess', gameState, broadcast=True)

# {
#    user: username,
#    roomId: roomid,
#    gameState: newGameState
# }

@socketio.on('join')
def handle_join(credentials):
    username = credentials['user']
    roomID = credentials['roomID']
    game_state = json.loads(redis_client.get(roomID))

    # TODO: handle disconnected player in else
    if game_state['gameStart'] == False:
        # TODO: account for existing username
        game_state['players'].append(username)
        redis_client.set(roomID, json.dumps(game_state))
        emit('join', json.loads(redis_client.get(roomID)), broadcast=True)

@socketio.on('start')
def handle_start(roomID):
    game_state = json.loads(redis_client.get(roomID))
    game_state['gameStart'] = True
    game_state['guesser'] = game_state["players"][1]
    print(f"here are the players: {game_state['players']}")
    redis_client.set(roomID, json.dumps(game_state))
    emit('start', json.loads(redis_client.get(roomID)), broadcast=True)


@app.route("/", methods=['GET','POST'])
def show_index():
    roomID = request.args.get("roomID", default="", type=str)
    if roomID and redis_client.exists(roomID):
        return json.loads(redis_client.get(roomID))
    return abort(404)

@socketio.on("create")
def create_game(request):
    # print("Creating room with params ", request)
    roomID = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k=10))
    while redis_client.exists(roomID):
        roomID = ''.join(random.choices(string.ascii_uppercase +
                                        string.digits, k=10))

    guessedWord = ['#' if c.isalnum() else c for c in request['word']]

    # TODO: Get word and category input at game screen
    defGameState = {'players': [request['username']],
                    'hanger': request['username'],
                    'category': request['category'],
                    'word': request['word'],
                    'guessedLetters': [],
                    'numIncorrect': 0,
                    'lives': int(request['lives']),
                    'guessedWords': [],
                    'guesser': None,
                    'curGuess': None,
                    'guessedWord': ''.join(guessedWord),
                    'gameStart': False,
                    }

    redis_client.set(roomID, json.dumps(defGameState))
    # print(roomID, redis_client.exists(roomID))

    response = {'gameState': defGameState, 'roomID': roomID}
    emit('link', response)

if __name__ == '__main__':
    socketio.run(app)
