from flask import Flask
from flask_socketio import SocketIO, send, emit
from flask_redis import FlaskRedis

import json
import string
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
app.config['REDIS_URL'] = "redis://:@localhost:6379/0"

socketio = SocketIO(app, cors_allowed_origins='*')
redis_client = FlaskRedis(app)


@socketio.on('message')
def handle_message(message):
    # print('received message: ', message)
    emit('response', message)


@socketio.on('create')
def create_game(request):
    # print("Creating room with params ", request)
    roomID = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k=10))
    while redis_client.get(roomID) == '(nil)':
        roomID = ''.join(random.choices(string.ascii_uppercase +
                                        string.digits, k=10))

    request = json.loads(request)

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
    url = f"http://localhost:3000/{roomID}/"
    # print(url)
    emit('link', url)


@app.route("/", methods=['POST'])
def index():
    return "hello"


if __name__ == '__main__':
    socketio.run(app)
