from . import socketio, redis_client
from flask_socketio import emit, join_room
import random
import json
import string


@socketio.on("create")
def create_game(params):
    while True:
        roomID = ''.join(random.choices(string.ascii_uppercase +
                                        string.digits, k=10))
        if not redis_client.exists(roomID):
            break

    def_game_state = {'players': [params['username']],
                      'hanger': params['username'],
                      'category': "",
                      'word': "",
                      'guessedLetters': [],
                      'numIncorrect': 0,
                      'lives': int(params['lives']),
                      'guessedWords': [],
                      'guesser': "",
                      'curGuess': "",
                      'guessedWord': "",
                      'gameStart': False,
                      'cap': 8,
                      'time': int(params['time']),
                      }

    join_room(roomID)
    print(f"{params['username']} has entered the room: {roomID}")

    redis_client.set(roomID, json.dumps(def_game_state))
    response = {'gameState': def_game_state, 'roomID': roomID}
    emit('link', response)
