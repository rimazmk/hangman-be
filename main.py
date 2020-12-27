from flask import Flask
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
redis_client = FlaskRedis(app)


@socketio.on('message')
def handle_message(message):
    # print('received message: ', message)
    emit('response', message)

@socketio.on('guess')
def handle_change(msg):
    msg = json.loads(msg)
    gameState = msg['gameState']
    cur = gameState['curGuess']

    if len(cur) == 1:
        gameState['guessedLetters'][ord(cur) - ord('a')] = True
        match = 0
        # Frontend prevents user from guessing a previously guessed letter
        for i, (w, g) in enumerate(zip(gameState['word'], gameState['guessedWord'])):
            if w == cur and g == '#':
                gameState['guessedWord'][i] = cur
                match += 1

        if not match:
            gameState['numIncorrect'] += 1

    else:
        gameState['guessedWords'].append(cur)

        if cur != gameState['word']:
            gameState['numIncorrect'] += 1

    # TODO: Use variable number of lives
    # TODO: Update wins variable here
    if cur == gameState['word'] or gameState['numIncorrect'] == 7 or gameState['word'] == gameState['guessedWord']:
        pass
    else:
        pass

    redis_client.set(msg['roomID'], gameState)
    emit('game', gameState, broadcast=True)

# {
#    user: username,
#    roomId: roomid,
#    gameState: newGameState
# }

@socketio.on('join')
def handle_join(credentials):
    credentials = json.loads(credentials)
    username = credentials['username']
    roomID = credentials['roomID']
    game_state = json.loads(redis_client.get(roomID))

    if game_state['gameStart'] == False:
        game_state['players'].append(username)
        redis_client.set(roomID,json.dumps(game_state))
        emit('joined',redis_client.get(roomID))


@app.route("/<code>",methods=['GET','POST'])
def join_game(code):
    # return game state 
    if redis.get(code) != '(nil)':
        emit('game', redis_client.get(code))

@app.route("/create", methods=["POST"])
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
    emit('link', url)



@app.route("/", methods=['GET','POST'])
def show_index():
    return "hello"



if __name__ == '__main__':
    socketio.run(app)
