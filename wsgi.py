import os
from hangman import app, socketio

if __name__ == "__main__":
    socketio.run(app, debug=True, port=4000)
