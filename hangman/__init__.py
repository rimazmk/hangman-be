from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_redis import FlaskRedis

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = FlaskRedis(app, decode_responses=True)

app.config['SECRET_KEY'] = b''.join([
    b'\x92\xc6\xd6',
    b'\x1e;\x19_fl\xc0',
    b'\xf31\xc1N\xc0kT',
    b'\xb0s\x7f\xa1',
    b'\x8f\x03',
])
app.config['REDIS_URL'] = "redis://:@localhost:6379/0"

cors = CORS(app)
socketio.init_app(app)

import hangman.db
import hangman.game
import hangman.routes
import hangman.sockets
