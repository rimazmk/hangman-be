from . import app, socketio
from flask_socketio import send, emit

@socketio.on('message')
def handle_message(message):
    print('received message: ', message)
    emit('response', message)

@app.route("/")
def index():
    return "hello"

if __name__ == '__main__':
    socketio.run(app)
