from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'
app.config['SECRET_KEY'] = 'secret!'

cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
socketio.run(app)

import hangman.sockets
import hangman.server
