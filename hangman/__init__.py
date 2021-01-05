"""Online Multiplayer Hangman Game."""

from typing import List, Dict, TypedDict
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/hangman"
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['SECRET_KEY'] = b''.join([
    b'\x92\xc6\xd6',
    b'\x1e;\x19_fl\xc0',
    b'\xf31\xc1N\xc0kT',
    b'\xb0s\x7f\xa1',
    b'\x8f\x03',
])

cors = CORS(app)
socketio.init_app(app)


class GameState(TypedDict):
    """Assist with type hinting for GameState object."""

    players: List[str]
    wins: Dict[str, int]
    hanger: str
    category: str
    word: str
    guessedLetters: List[str]
    numIncorrect: int
    lives: int
    guessedWords: List[str]
    guesser: str
    curGuess: str
    guessedWord: str
    gameStart: bool
    cap: int
    rotation: str
    round: int
    numRounds: int
    time: int


from . import db, game, routes, sockets
