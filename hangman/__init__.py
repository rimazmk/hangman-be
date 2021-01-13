"""Online Multiplayer Hangman Game."""

import os
from os.path import join, dirname
from dotenv import load_dotenv
from typing import List, Dict, TypedDict
from flask import Flask
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["CORS_SUPPORTS_CREDENTIALS"]=True
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail= Mail(app)
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins=os.getenv("CLIENT_ORIGIN"))

app.config['SECRET_KEY'] = b''.join([
    b'\x92\xc6\xd6',
    b'\x1e;\x19_fl\xc0',
    b'\xf31\xc1N\xc0kT',
    b'\xb0s\x7f\xa1',
    b'\x8f\x03',
])

cors = CORS(app, support_credentials=True, origins=[os.getenv("CLIENT_ORIGIN")])
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
