from flask import Flask
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(message):
    print('received message: ', message)
    emit('response', message, broadcast=True)

@app.route("/")
def index():
    return "hello"

if __name__ == '__main__':
    socketio.run(app)
