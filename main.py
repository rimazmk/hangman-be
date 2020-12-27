from flask import Flask, abort
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

socketio = SocketIO(app, cors_allowed_origins='*', logger=True, engineio_logger=True)
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

@socketio.on('guess')
def handle_change(msg):
    gameState = msg['gameState']
    cur = gameState['curGuess']

    if len(cur) == 1:
        gameState['guessedLetters'][ord(cur) - ord('a')] = True
        match = 0
        # Frontend prevents user from guessing a previously guessed letter
        for i, (w, g) in enumerate(zip(gameState['word'], gameState['guessedWord'])):
            if w == cur and g == '#':
                gameState['guessedWord'] = gameState['guessedWord'][:i] + cur + gameState['guessedWord'][i + 1:]
                match += 1

        if match == 0:
            gameState['numIncorrect'] += 1

    else:
        gameState['guessedWords'].append(cur)

        if cur.lower() != gameState['word'].lower():
            gameState['numIncorrect'] += 1

    # TODO: Use variable number of lives
    # TODO: Update wins variable here
    if cur == gameState['word'] or gameState['numIncorrect'] == 7 or gameState['word'].lower() == gameState['guessedWord'].lower():
        gameState['hanger'] = msg['user']
        gameState['category'] = ""
        gameState['word'] = ""
        gameState['guessedLetters'] = [False] * 26
        gameState['numIncorrect'] = 0
        gameState['guessedWords'] = []
        gameState['curGuess'] = ""
        gameState['guessedWord'] = []

    hangPos = gameState['players'].index(gameState['hanger'])
    guessPos = hangPos + 1 if hangPos != (len(gameState['players']) - 1) else 0
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
        emit('joined', redis_client.get(roomID))

@socketio.on('start')
def handle_start(start_msg):
    roomID = start_msg['roomID']
    game_state = json.loads(redis_client.get(roomID))
    game_state['gameStart'] = True
    redis_client.set(roomID, json.dumps(game_state))
    emit('started', redis_client.get(roomID))

@app.route("/", methods=['GET','POST'])
def show_index():
    return "hello"

@socketio.on("create")
def create_game(request):
    # print("Creating room with params ", request)
    roomID = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k=10))
    while redis_client.exists(roomID):
        roomID = ''.join(random.choices(string.ascii_uppercase +
                                        string.digits, k=10))

    # TODO: Get word and category input at game screen
    defGameState = {'players': [request['username']],
                    'hanger': request['username'],
                    'category': request['category'],
                    'word': request['word'],
                    'guessedLetters': [False] * 26,
                    'numIncorrect': 0,
                    'guessedWords': [],
                    'guesser': None,
                    'curGuess': None,
                    'guessedWord': '#' * len(request['word']),
                    'gameStart': False,
                    }

    redis_client.set(roomID, json.dumps(defGameState))
    # print(roomID, redis_client.exists(roomID))
    url = f"http://localhost:3000/{roomID}/"

    response = {'gameState': defGameState, 'url': url}
    emit('link', response)

@app.route("/room/<code>/", methods=['GET'])
def get_state(code):
    # print("received get request", code)
    if redis_client.exists(code):
        # print(redis_client.get(code))
        return json.loads(redis_client.get(code))

    return abort(404)

# if __name__ == '__main__':
#     socketio.run(app)
